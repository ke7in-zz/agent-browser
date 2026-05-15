#!/usr/bin/env python3
"""
SoundCloud Outreach Engine — CDP-based messaging automation.

Used by the soundcloud-outreach pi skill. Not run standalone by operators.
Requires Chrome with CDP on 100.64.0.5:9222 and an active SoundCloud session.
"""

import base64
import json
import os
import socket
import struct
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

CDP = "http://100.64.0.5:9222"
SKILL_DIR = Path(__file__).parent
EXCLUSIONS_FILE = SKILL_DIR / "exclusions.yaml"
QUEUE_FILE = Path("/tmp/sc_outreach_queue.json")
PROGRESS_FILE = Path("/tmp/sc_outreach_progress.json")

# Rate limit tuning
DELAY_BETWEEN_SENDS = 12
PAUSE_AFTER_3_FAILS = 300      # 5 min
PAUSE_AFTER_5_FAILS = 1800     # 30 min
MAX_CONSECUTIVE_FAILS = 10
MAX_SENDS_PER_SESSION = 18


# --- WebSocket CDP client ---

def _recvall(sock, n):
    b = b""
    while len(b) < n:
        chunk = sock.recv(n - len(b))
        if not chunk:
            raise EOFError
        b += chunk
    return b


class CDPClient:
    def __init__(self):
        ws_url = self._get_page_ws()
        u = urllib.parse.urlparse(ws_url)
        self.sock = socket.create_connection((u.hostname, u.port or 80), timeout=30)
        self.sock.settimeout(30)
        key = base64.b64encode(os.urandom(16)).decode()
        path = u.path + ("?" + u.query if u.query else "")
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {u.hostname}:{u.port}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            resp += self.sock.recv(4096)
        self._msg_id = 0

    @staticmethod
    def _get_page_ws():
        data = json.load(urllib.request.urlopen(CDP + "/json/list", timeout=5))
        pages = [p for p in data if p.get("type") == "page"]
        if not pages:
            raise RuntimeError("No browser page found via CDP")
        return pages[0]["webSocketDebuggerUrl"]

    def _send_frame(self, payload: bytes):
        hdr = bytearray([0x81])
        n = len(payload)
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126)
            hdr += struct.pack("!H", n)
        else:
            hdr.append(0x80 | 127)
            hdr += struct.pack("!Q", n)
        mask = os.urandom(4)
        hdr += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(hdr + masked)

    def _recv_frame(self) -> str:
        while True:
            b1, b2 = _recvall(self.sock, 2)
            op = b1 & 0xF
            masked = b2 & 0x80
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack("!H", _recvall(self.sock, 2))[0]
            elif n == 127:
                n = struct.unpack("!Q", _recvall(self.sock, 8))[0]
            mask = _recvall(self.sock, 4) if masked else b""
            data = _recvall(self.sock, n)
            if masked:
                data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
            if op == 1:
                return data.decode()
            if op == 8:
                raise EOFError("WS closed")
            if op == 9:
                self.sock.sendall(b"\x8a\x00")

    def call(self, method: str, params: dict | None = None) -> dict:
        self._msg_id += 1
        mid = self._msg_id
        self._send_frame(json.dumps({"id": mid, "method": method, "params": params or {}}).encode())
        while True:
            msg = json.loads(self._recv_frame())
            if msg.get("id") == mid:
                return msg

    def evaluate(self, expr: str):
        r = self.call("Runtime.evaluate", {"expression": expr, "awaitPromise": True, "returnByValue": True})
        return r.get("result", {}).get("result", {}).get("value")

    def navigate(self, url: str):
        self.call("Page.navigate", {"url": url})


# --- Exclusion list ---

def load_exclusions() -> set[str]:
    if not EXCLUSIONS_FILE.exists():
        return set()
    text = EXCLUSIONS_FILE.read_text()
    slugs = set()
    in_list = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("excluded_slugs:"):
            in_list = True
            continue
        if in_list:
            if stripped.startswith("- "):
                slug = stripped[2:].split("#")[0].strip()
                if slug:
                    slugs.add(slug)
            elif stripped and not stripped.startswith("#"):
                break
    return slugs


# --- Audience building ---

def get_client_id() -> str:
    return "gxPRNsEq7CDD7Wvem4iymWOq3YfU7KS8"


def get_user_id() -> int:
    return 366319


def fetch_likers(cid: str, uid: int) -> list[dict]:
    """Fetch unique likers across all public tracks from the last 3 years."""
    cutoff = datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year - 3)

    # Get tracks
    url = f"https://api-v2.soundcloud.com/users/{uid}/tracks?" + urllib.parse.urlencode(
        {"client_id": cid, "limit": 100, "offset": 0, "linked_partitioning": "1", "app_version": "1778677443", "app_locale": "en"}
    )
    tracks = []
    while url:
        data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
        tracks += data.get("collection", [])
        url = data.get("next_href")
        if url and "client_id=" not in url:
            url += ("&" if "?" in url else "?") + "client_id=" + cid

    # Filter to recent public original tracks
    selected = []
    for t in tracks:
        dt = datetime.fromisoformat((t.get("display_date") or t.get("created_at")).replace("Z", "+00:00"))
        if dt >= cutoff and t.get("sharing") == "public" and t.get("user_id") == uid and (t.get("likes_count") or 0) > 0:
            selected.append(t)

    # Collect likers
    users = {}
    for t in selected:
        tid = t["id"]
        url = f"https://api-v2.soundcloud.com/tracks/{tid}/likers?" + urllib.parse.urlencode(
            {"client_id": cid, "limit": 200, "offset": 0, "linked_partitioning": "1", "app_version": "1778677443", "app_locale": "en"}
        )
        while url:
            try:
                data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
            except urllib.error.HTTPError:
                break
            for u in data.get("collection", []):
                uid2 = u.get("id")
                if uid2 not in users:
                    users[uid2] = {"slug": u.get("permalink"), "username": u.get("username"), "url": u.get("permalink_url")}
            url = data.get("next_href")
            if url and "client_id=" not in url:
                url += ("&" if "?" in url else "?") + "client_id=" + cid

    return list(users.values())


def fetch_followers(cid: str, uid: int) -> list[dict]:
    """Fetch all followers."""
    users = {}
    url = f"https://api-v2.soundcloud.com/users/{uid}/followers?" + urllib.parse.urlencode(
        {"client_id": cid, "limit": 200, "offset": 0, "linked_partitioning": "1", "app_version": "1778677443", "app_locale": "en"}
    )
    while url:
        try:
            data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20))
        except urllib.error.HTTPError:
            break
        for u in data.get("collection", []):
            uid2 = u.get("id")
            if uid2 not in users:
                users[uid2] = {"slug": u.get("permalink"), "username": u.get("username"), "url": u.get("permalink_url")}
        url = data.get("next_href")
        if url and "client_id=" not in url:
            url += ("&" if "?" in url else "?") + "client_id=" + cid

    return list(users.values())


# --- Track resolution ---

def resolve_track(cdp: CDPClient, track_query: str) -> str | None:
    """Find the track share URL (with secret token if private) from the browser session."""
    token = cdp.evaluate(
        "JSON.parse(localStorage.getItem('V2::local::broadcast')).broadcast.args[0]"
    )
    if not token:
        return None

    result = cdp.evaluate(f"""
        fetch('https://api-v2.soundcloud.com/me/shortcuts/own-tracks?client_id={get_client_id()}&limit=50&offset=0&linked_partitioning=1&app_version=1778677443&app_locale=en',
            {{headers:{{Authorization:'OAuth {token}'}}}})
        .then(r=>r.json())
        .then(d=>d.collection.map(t=>({{title:t.title,url:t.permalink_url,secret:t.secret_token}})))
    """)
    if not result:
        return None

    query_lower = track_query.lower()
    for t in result:
        if query_lower in t.get("title", "").lower():
            url = t["url"]
            secret = t.get("secret")
            if secret and secret not in url:
                url += "/" + secret
            return url
    return None


# --- Message sending ---

def send_one_message(cdp: CDPClient, slug: str, message_with_url: str) -> str:
    """Send a single message via the SoundCloud UI. Returns status string."""
    # Close any stale modal
    cdp.evaluate("(() => { const c=document.querySelector('.modal__closeButton'); if(c) c.click(); })()")
    time.sleep(1)

    # Navigate to profile
    cdp.navigate(f"https://soundcloud.com/{slug}")
    time.sleep(5)

    # Click message button
    result = cdp.evaluate(
        "(() => { const btn=document.querySelector('.sc-button-message'); "
        "if(!btn) return 'no_btn'; btn.click(); return 'ok'; })()"
    )
    if result != "ok":
        return "SKIP_NO_BUTTON"
    time.sleep(3)

    # Verify modal
    modal = cdp.evaluate("document.querySelector('.modal.showBackground')?.innerText || ''")
    if "New message" not in str(modal):
        return "SKIP_NO_MODAL"

    # Type message
    escaped = message_with_url.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    cdp.evaluate(
        f"(() => {{ const ta=document.querySelector('textarea.textfield__input'); "
        f"if(!ta) return null; ta.focus(); ta.value='{escaped}'; "
        f"ta.dispatchEvent(new Event('input',{{bubbles:true}})); "
        f"ta.dispatchEvent(new Event('change',{{bubbles:true}})); }})()"
    )
    time.sleep(3)

    # Check track auto-attached
    modal2 = cdp.evaluate("document.querySelector('.modal.showBackground')?.innerText || ''")
    if "Raw Style Synergy" not in str(modal2) and "supermōdal" not in str(modal2):
        # Try manual search
        cdp.evaluate("(() => { const b=document.querySelector('.composeMessage__addSoundButton'); if(b)b.click(); })()")
        time.sleep(2)
        cdp.evaluate(
            "(() => { const i=document.querySelector('.userAudibleSearch__input'); "
            "if(!i) return; i.focus(); i.value='raw style synergy'; "
            "i.dispatchEvent(new Event('input',{bubbles:true})); "
            "i.dispatchEvent(new Event('change',{bubbles:true})); })()"
        )
        time.sleep(3)
        cdp.evaluate(
            "(() => { const item=document.querySelector('.userAudibleSearchResults__item .userAudibleSearchResultItem'); "
            "if(item) item.click(); })()"
        )
        time.sleep(2)

    # Click Send
    cdp.evaluate("document.querySelector('.composeMessage__sendButton').click()")
    time.sleep(5)

    # Check success
    body_tail = cdp.evaluate("document.body.innerText.slice(-500)") or ""
    if "was sent successfully" in body_tail:
        return "SENT"

    modal3 = cdp.evaluate("document.querySelector('.modal.showBackground')?.innerText || null")
    if modal3 is None:
        return "SENT"

    return "FAILED"


# --- Orchestrator ---

def run_outreach(audience: str, track_query: str, message: str, dry_run: bool = False, resume: bool = False):
    """Main orchestration function."""
    cid = get_client_id()
    uid = get_user_id()
    exclusions = load_exclusions()

    # Load or build queue
    if resume and QUEUE_FILE.exists():
        queue_data = json.loads(QUEUE_FILE.read_text())
        audience_list = queue_data["remaining"]
        track_url = queue_data["track_url"]
        print(f"Resuming: {len(audience_list)} remaining")
    else:
        print(f"Building audience ({audience})...")
        if audience == "likers":
            raw_list = fetch_likers(cid, uid)
        elif audience == "followers":
            raw_list = fetch_followers(cid, uid)
        else:
            raise ValueError(f"Unknown audience: {audience}. Use 'likers' or 'followers'.")

        # Filter exclusions
        audience_list = [u for u in raw_list if u["slug"] not in exclusions]
        print(f"Audience: {len(raw_list)} total, {len(audience_list)} after exclusions")

        # Resolve track
        print(f"Resolving track: {track_query}...")
        cdp = CDPClient()
        track_url = resolve_track(cdp, track_query)
        if not track_url:
            print(f"ERROR: Track '{track_query}' not found in your library.")
            return
        print(f"Track URL: {track_url}")

        # Save queue
        queue_data = {
            "audience": audience,
            "track_query": track_query,
            "track_url": track_url,
            "message": message,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "remaining": audience_list,
            "sent": [],
            "skipped": [],
            "failed": [],
        }
        QUEUE_FILE.write_text(json.dumps(queue_data, indent=2, ensure_ascii=False))

    if dry_run:
        print("\n--- DRY RUN ---")
        print(f"Would send to {len(audience_list)} accounts")
        print(f"Track: {track_url}")
        print(f"Message: {message[:80]}...")
        for i, u in enumerate(audience_list[:20], 1):
            print(f"  {i}. {u['username']} — {u['url']}")
        if len(audience_list) > 20:
            print(f"  ... and {len(audience_list) - 20} more")
        return

    # Build message with track URL
    message_with_url = message.rstrip() + "\n" + track_url + " "

    # Send
    cdp = CDPClient()
    sent = queue_data.get("sent", [])
    skipped = queue_data.get("skipped", [])
    failed = queue_data.get("failed", [])
    consecutive_fails = 0
    sends_this_session = 0

    remaining = list(audience_list)
    for i, user in enumerate(remaining):
        if sends_this_session >= MAX_SENDS_PER_SESSION:
            print(f"\nSession cap reached ({MAX_SENDS_PER_SESSION} sends). Save and stop.")
            break

        slug = user["slug"]
        name = user["username"]
        print(f"[{i+1}/{len(remaining)}] {name} ({slug})...", end=" ", flush=True)

        status = send_one_message(cdp, slug, message_with_url)
        print(status)

        if status == "SENT":
            sent.append(user)
            consecutive_fails = 0
            sends_this_session += 1
            time.sleep(DELAY_BETWEEN_SENDS)
        elif status.startswith("SKIP"):
            skipped.append({**user, "reason": status})
            consecutive_fails = 0
            time.sleep(3)
        else:
            failed.append(user)
            consecutive_fails += 1
            if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                print(f"\n{MAX_CONSECUTIVE_FAILS} consecutive failures. Stopping.")
                break
            elif consecutive_fails >= 5:
                print(f"  Pausing {PAUSE_AFTER_5_FAILS}s...")
                time.sleep(PAUSE_AFTER_5_FAILS)
            elif consecutive_fails >= 3:
                print(f"  Pausing {PAUSE_AFTER_3_FAILS}s...")
                time.sleep(PAUSE_AFTER_3_FAILS)
            else:
                time.sleep(5)

    # Update queue with remaining
    already_processed = {u["slug"] for u in sent + skipped + failed}
    still_remaining = [u for u in audience_list if u["slug"] not in already_processed]

    queue_data["sent"] = sent
    queue_data["skipped"] = skipped
    queue_data["failed"] = failed
    queue_data["remaining"] = still_remaining
    QUEUE_FILE.write_text(json.dumps(queue_data, indent=2, ensure_ascii=False))

    # Report
    print(f"\n{'='*50}")
    print("## SoundCloud Outreach Report")
    print("")
    print(f"Audience: {audience}")
    print(f"Track: {track_query} ({track_url})")
    print(f"Message: {message[:80]}...")
    print("")
    print("| Status | Count |")
    print("|--------|-------|")
    print(f"| Sent | {len(sent)} |")
    print(f"| Skipped | {len(skipped)} |")
    print(f"| Failed (rate limited) | {len(failed)} |")
    print(f"| Remaining | {len(still_remaining)} |")
    print("")
    if sent:
        print("Sent to:")
        for u in sent[-20:]:
            print(f"  ✓ {u['username']} — {u['url']}")
    if still_remaining:
        print(f"\nResume with: /skill:soundcloud-outreach {audience} --resume")
    print(f"\nQueue: {QUEUE_FILE}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SoundCloud outreach engine")
    parser.add_argument("audience", choices=["likers", "followers"])
    parser.add_argument("--attach", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run_outreach(args.audience, args.attach, args.message, args.dry_run, args.resume)
