# SoundCloud Outreach

## Model

Required preset: **`build`** — `anthropic-hai/claude-opus-4-6`, medium thinking, full tools.

If the active model is not `claude-opus-4-6`, switch before executing any step:

- Invoked via `/skill:`: run `/preset build` first.
- Invoked via natural language: run `/preset build` now, then proceed.

---

Automate fan engagement messaging on SoundCloud. Builds audience lists from track likers or account followers, applies exclusions, sends messages with track attachments respecting rate limits, and produces a summary report.

## Inputs

```
/skill:soundcloud-outreach <audience> --attach "<track name>" --message "<body>"
```

### Arguments

| Argument    | Required | Description                                                                                                        |
| ----------- | -------- | ------------------------------------------------------------------------------------------------------------------ |
| `audience`  | yes      | One of: `likers` (people who liked your public tracks in the last 3 years) or `followers` (your account followers) |
| `--attach`  | yes      | Track name to attach via "add track or playlist" (matched from your own tracks)                                    |
| `--message` | yes      | Message body text                                                                                                  |
| `--resume`  | no       | Resume a previously interrupted run from the queue file                                                            |
| `--dry-run` | no       | Build the list and show the plan without sending                                                                   |
| `--status`  | no       | Report progress of the active queue without sending                                                                |

## Prerequisites

- Chrome running on Windows host with CDP enabled at `http://100.64.0.5:9222`
- Logged into SoundCloud in the browser
- The attached track must exist in your SoundCloud library (private or public)

## Exclusion List

Maintained in `.pi/skills/soundcloud-outreach/exclusions.yaml`. These accounts are never messaged:

```yaml
excluded_slugs:
  - funkybeans
  - ryan-lee-234065614
  - morankj # driftsett
  - supermoda1 # self
  - astronavis
```

To add exclusions, edit the file directly. Use the SoundCloud URL slug (the part after `soundcloud.com/`).

## Workflow

### Phase 1: Build Audience

1. Resolve your SoundCloud user ID and client ID from the browser session.
2. Depending on `audience`:
   - **likers**: Fetch all your public tracks from the last 3 years. For each track with likes > 0, paginate `/tracks/{id}/likers` to collect all unique accounts.
   - **followers**: Paginate `/users/{id}/followers` to collect all follower accounts.
3. Deduplicate by user ID.
4. Remove excluded accounts (from `exclusions.yaml`).
5. Remove already-messaged accounts (from the current run's sent log).
6. Save the audience list to `/tmp/sc_outreach_queue.json`.

### Phase 2: Resolve Track Attachment

1. Fetch your own tracks (including private) using the browser's OAuth token.
2. Match `--attach` argument against track titles (case-insensitive substring match).
3. Extract the track's share URL (including secret token for private tracks).
4. Verify the track appears in the browser's "add track or playlist" search.

### Phase 3: Send Messages

For each recipient in the queue:

1. Navigate to the recipient's profile page.
2. Click the "Message" button to open the compose dialog.
3. Type the message body (with track URL appended for auto-attachment).
4. Verify the track card appears in the compose area.
5. Click "Send".
6. Verify success (toast message or modal closure).
7. Log the result to `/tmp/sc_outreach_progress.json`.

**Rate limit handling:**

- Wait 12 seconds between successful sends.
- After 3 consecutive failures/uncertain results, pause for 5 minutes.
- After 5 consecutive failures, pause for 30 minutes.
- After 10 consecutive failures, stop the run and report. The queue can be resumed later with `--resume`.
- Maximum ~18 messages per session to stay within SoundCloud's daily cap.
- When the daily cap is hit, save progress and report remaining count.

### Phase 4: Summary Report

At the end of each run (or when stopped by rate limits), output:

```
## SoundCloud Outreach Report

Audience: likers | followers
Track attached: <track name>
Message: <first 80 chars>...

| Status | Count |
|--------|-------|
| Sent | N |
| Skipped (no message button) | N |
| Skipped (excluded) | N |
| Failed (rate limited) | N |
| Remaining | N |

Sent to:
1. Username — https://soundcloud.com/slug
2. ...

Remaining (resume with --resume):
- Username — https://soundcloud.com/slug
- ...

Queue file: /tmp/sc_outreach_queue.json
Progress file: /tmp/sc_outreach_progress.json
```

## Rate Limit Strategy

SoundCloud enforces approximately 20 messages per 24-hour window. This skill:

- **Respects** the limit rather than evading it.
- **Detects** when the limit is hit (modal stays open after send click, or error toast).
- **Pauses and saves state** so the run can resume in the next session.
- **Reports** how many remain and the recommended wait time.

For large audiences (>20), expect the skill to complete across multiple sessions/days.

## File Outputs

| File                                             | Purpose                             |
| ------------------------------------------------ | ----------------------------------- |
| `/tmp/sc_outreach_queue.json`                    | Full audience list with send status |
| `/tmp/sc_outreach_progress.json`                 | Per-recipient send results          |
| `.pi/skills/soundcloud-outreach/exclusions.yaml` | Permanent do-not-message list       |

## Examples

```
# Message all track likers
/skill:soundcloud-outreach likers \
  --attach "Raw Style Synergy" \
  --message "Appreciate the like and the support! Here's a sneak peak at a new track before it goes public."

# Message followers with a different track
/skill:soundcloud-outreach followers \
  --attach "Officially Missing You" \
  --message "Hey! Thanks for following. Check out my latest remix — would love your feedback."

# Resume an interrupted run
/skill:soundcloud-outreach likers --resume

# Check progress of the active queue
/skill:soundcloud-outreach --status

# Preview the list without sending
/skill:soundcloud-outreach likers --attach "Raw Style Synergy" --message "..." --dry-run
```

## Error Handling

| Scenario                     | Behavior                                             |
| ---------------------------- | ---------------------------------------------------- |
| No CDP connection            | Stop with connection error                           |
| Not logged into SoundCloud   | Stop with auth error                                 |
| Track not found in library   | Stop with track-not-found error                      |
| User has no "Message" button | Skip, log as "no message button"                     |
| Rate limited mid-run         | Save progress, report remaining, suggest resume time |
| Browser page crash           | Attempt reconnect once, then stop                    |

## Approval Model

This skill operates under blanket operator approval for the send action. The operator invokes the skill with a specific audience, message, and track — that invocation IS the approval for all sends in that run. Individual per-recipient approval is not required.

If the operator wants to review before sending, use `--dry-run` first.
