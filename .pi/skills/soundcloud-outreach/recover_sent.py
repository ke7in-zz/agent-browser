#!/usr/bin/env python3
"""
Recover the list of accounts messaged in a recent outreach run by querying
SoundCloud's conversations API via CDP.

Usage:
    python3 recover_sent.py [--days 2]

Outputs the list and optionally writes to state/sent_history.json.
"""

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from engine import CDPClient, get_client_id, get_user_id

STATE_DIR = Path(__file__).parent / "state"
SENT_HISTORY = STATE_DIR / "sent_history.json"


def get_oauth_token(cdp: CDPClient) -> str:
    """Intercept OAuth token from SoundCloud API requests via CDP Fetch domain."""
    import time

    cdp.call(
        "Fetch.enable",
        {
            "patterns": [
                {
                    "urlPattern": "*api-v2.soundcloud.com*",
                    "requestStage": "Request",
                }
            ]
        },
    )
    cdp.navigate("https://soundcloud.com/discover")

    token = None
    start = time.time()
    while time.time() - start < 15:
        try:
            msg = json.loads(cdp._recv_frame())
            if msg.get("method") == "Fetch.requestPaused":
                params = msg.get("params", {})
                headers = params.get("request", {}).get("headers", {})
                auth = headers.get("Authorization") or headers.get("authorization")
                if auth and "OAuth" in auth:
                    token = auth.replace("OAuth ", "")
                    cdp.call(
                        "Fetch.continueRequest", {"requestId": params["requestId"]}
                    )
                    break
                cdp.call("Fetch.continueRequest", {"requestId": params["requestId"]})
        except Exception:
            break

    cdp.call("Fetch.disable")
    return token


def fetch_conversations(
    token: str, client_id: str, user_id: int, since_days: int = 2
) -> list[dict]:
    """Fetch recent conversations from SoundCloud API."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)

    url = (
        f"https://api-v2.soundcloud.com/users/{user_id}/conversations?"
        + urllib.parse.urlencode(
            {
                "client_id": client_id,
                "limit": 50,
                "offset": 0,
                "linked_partitioning": "1",
                "app_version": "1778677443",
                "app_locale": "en",
            }
        )
    )

    conversations = []
    while url:
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"OAuth {token}",
                "User-Agent": "Mozilla/5.0",
            },
        )
        try:
            data = json.load(urllib.request.urlopen(req, timeout=20))
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            break

        for conv in data.get("collection", []):
            last_msg_at = conv.get("last_message", {}).get("created_at", "")
            if last_msg_at:
                dt = datetime.fromisoformat(last_msg_at.replace("Z", "+00:00"))
                if dt < cutoff:
                    # Past our window, stop
                    return conversations
            conversations.append(conv)

        url = data.get("next_href")
        if url and "client_id=" not in url:
            url += ("&" if "?" in url else "?") + "client_id=" + client_id

    return conversations


def extract_outreach_recipients(
    conversations: list[dict], my_uid: int, message_prefix: str = ""
) -> list[int]:
    """Extract user IDs of outreach recipients from conversations."""
    other_uids = []
    for conv in conversations:
        last_msg = conv.get("last_message", {})
        content = last_msg.get("content", "")
        if message_prefix and message_prefix not in content:
            continue
        conv_id = conv.get("id", "")
        parts = conv_id.split(":")
        if len(parts) == 2:
            other_uid = int(parts[0]) if int(parts[0]) != my_uid else int(parts[1])
            other_uids.append(other_uid)
    return other_uids


def resolve_user_ids(uids: list[int], token: str, client_id: str) -> list[dict]:
    """Resolve user IDs to profile info."""
    users = []
    for uid in uids:
        url = (
            f"https://api-v2.soundcloud.com/users/{uid}"
            f"?client_id={client_id}&app_version=1778677443&app_locale=en"
        )
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"OAuth {token}",
                "User-Agent": "Mozilla/5.0",
            },
        )
        try:
            u = json.load(urllib.request.urlopen(req, timeout=10))
            users.append(
                {
                    "slug": u.get("permalink"),
                    "username": u.get("username"),
                    "url": u.get("permalink_url"),
                    "user_id": u.get("id"),
                }
            )
        except Exception as e:
            print(f"  ✗ uid={uid} — {e}")
    return users


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=2, help="Look back N days")
    parser.add_argument("--save", action="store_true", help="Save to sent_history.json")
    args = parser.parse_args()

    print("Connecting to CDP...")
    cdp = CDPClient()

    # Navigate to SoundCloud if not already there
    current_url = cdp.evaluate("window.location.href") or ""
    if "soundcloud.com" not in current_url:
        print("Navigating to SoundCloud...")
        cdp.navigate("https://soundcloud.com")
        import time

        time.sleep(5)

    print("Extracting OAuth token...")
    token = get_oauth_token(cdp)
    if not token:
        print("ERROR: Could not extract OAuth token. Are you logged in?")
        sys.exit(1)
    print(f"Token: {token[:8]}...")

    client_id = get_client_id()
    my_uid = get_user_id()

    print(f"Fetching conversations from the last {args.days} days...")
    conversations = fetch_conversations(token, client_id, my_uid, args.days)
    print(f"Found {len(conversations)} recent conversations")

    outreach_uids = extract_outreach_recipients(
        conversations, my_uid, "Appreciate the like and the support"
    )
    print(f"Outreach messages identified: {len(outreach_uids)}")

    if not outreach_uids:
        print("No outreach messages found in the time window.")
        return []

    print("Resolving user profiles...")
    recipients = resolve_user_ids(outreach_uids, token, client_id)

    print(f"\n{'=' * 50}")
    print(f"Accounts messaged in the last {args.days} days:")
    print(f"{'=' * 50}\n")

    for i, r in enumerate(recipients, 1):
        print(f"  {i:2}. {r['username']:<30} https://soundcloud.com/{r['slug']}")

    print(f"\nTotal: {len(recipients)}")

    if args.save:
        STATE_DIR.mkdir(parents=True, exist_ok=True)

        # Load existing history
        history = []
        if SENT_HISTORY.exists():
            history = json.loads(SENT_HISTORY.read_text())

        # Merge (dedupe by slug)
        existing_slugs = {r["slug"] for r in history}
        now = datetime.now(timezone.utc).isoformat()
        for r in recipients:
            if r["slug"] not in existing_slugs:
                history.append({**r, "sent_at": now, "source": "recovered"})
                existing_slugs.add(r["slug"])

        SENT_HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False))
        print(f"\nSaved to {SENT_HISTORY} ({len(history)} total entries)")

    return recipients


if __name__ == "__main__":
    main()
