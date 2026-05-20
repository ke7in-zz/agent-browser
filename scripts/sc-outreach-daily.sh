#!/bin/bash
# SoundCloud outreach daily runner — called by cron.
# Checks prerequisites, runs the engine with --resume, logs results.
set -euo pipefail

STATE_DIR="/home/ke7in/Projects/agent-browser/.pi/skills/soundcloud-outreach/state"
LOG="$STATE_DIR/cron.log"
ENGINE="/home/ke7in/Projects/agent-browser/.pi/skills/soundcloud-outreach/engine.py"
QUEUE="$STATE_DIR/queue.json"
CDP_URL="http://100.64.0.5:9222/json/version"
CHROME_START_SCRIPT="D:\\Projects\\agent-browser\\start-agent-chrome.ps1"

log() { echo "[$(date -Iseconds)] $*" >>"$LOG"; }

cdp_reachable() {
	curl -sf --max-time 5 "$CDP_URL" >/dev/null 2>&1
}

start_windows_chrome() {
	if ! command -v powershell.exe >/dev/null 2>&1; then
		log "ABORT: Chrome CDP not reachable and powershell.exe is unavailable"
		return 1
	fi

	log "CDP not reachable; launching Windows Chrome via $CHROME_START_SCRIPT"
	powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$CHROME_START_SCRIPT" >>"$LOG" 2>&1 || return 1

	for _ in {1..10}; do
		cdp_reachable && return 0
		sleep 2
	done

	return 1
}

# --- Preflight checks ---

# 1. CDP reachable? Launch Chrome on the Windows host if needed.
if ! cdp_reachable && ! start_windows_chrome; then
	log "ABORT: Chrome CDP not reachable at 100.64.0.5:9222"
	exit 1
fi

# 2. Queue file exists with remaining work?
if [ ! -f "$QUEUE" ]; then
	log "ABORT: No queue file at $QUEUE — nothing to resume"
	exit 0
fi

remaining=$(python3 -c "import json; d=json.load(open('$QUEUE')); print(len(d.get('remaining',[])))" 2>/dev/null || echo "0")
if [ "$remaining" = "0" ]; then
	log "DONE: Queue is empty — all messages sent"
	exit 0
fi

# 3. SoundCloud session active? (check via page title after nav)
session_check=$(python3 -c "
import json, urllib.request
data=json.load(urllib.request.urlopen('http://100.64.0.5:9222/json/list', timeout=5))
pages=[p for p in data if p.get('type')=='page']
if not pages: print('no_page')
elif 'soundcloud' in (pages[0].get('url','') + pages[0].get('title','')).lower(): print('ok')
else: print('ok')  # page might be on another site, engine will navigate
" 2>/dev/null || echo "error")

if [ "$session_check" = "no_page" ]; then
	log "ABORT: No browser page available via CDP"
	exit 1
fi

# --- Run engine ---

log "START: $remaining recipients remaining"

cd /home/ke7in/Projects/agent-browser
output=$(python3 "$ENGINE" likers \
	--attach "Raw Style Synergy" \
	--message "Appreciate the like and the support! Here's a sneak peak at a new track before it goes public. It's a cheeky remix and mash-up of Afro Puffs and a Mos Def freestyle I ripped from YouTube =) Let me know what you think!" \
	--resume 2>&1) || true

# Extract summary line
sent=$(echo "$output" | grep -oP 'Sent\s*\|\s*\K\d+' || echo "0")
new_remaining=$(python3 -c "import json; d=json.load(open('$QUEUE')); print(len(d.get('remaining',[])))" 2>/dev/null || echo "?")

log "FINISH: sent=$sent remaining=$new_remaining"

# Append full output for debugging
echo "$output" >>"$LOG"
echo "---" >>"$LOG"
