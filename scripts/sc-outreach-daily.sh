#!/bin/bash
# SoundCloud outreach daily runner — called by cron.
# Checks prerequisites, runs the engine with --resume, logs results.
set -euo pipefail

LOG="/tmp/sc_outreach_cron.log"
ENGINE="/home/ke7in/Projects/agent-browser/.pi/skills/soundcloud-outreach/engine.py"
QUEUE="/tmp/sc_outreach_queue.json"

log() { echo "[$(date -Iseconds)] $*" >>"$LOG"; }

# --- Preflight checks ---

# 1. CDP reachable?
if ! curl -sf --max-time 5 http://100.64.0.5:9222/json/version >/dev/null 2>&1; then
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
