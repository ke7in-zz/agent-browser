# Failure Patterns

<!-- This file records durable failure patterns observed during spec and bug
     workflows. It lives at .codex/memory/failure_patterns.md in each project
     repo and is created on first write by the emitting skill.

     PURPOSE: Prevent agents from repeating known dead-end approaches across
     sessions. Entries are structured so skills can read them at startup and
     surface relevant traps before beginning implementation or analysis.

     CONVENTIONS:
     - Append-only for new entries. Do not delete entries.
     - Supersession: when a new entry contradicts an active entry, mark the old
       entry's status as "superseded" and add a superseded_by reference. Do not
       remove the old entry — it serves as an audit trail.
     - Write filter: only persist patterns that are repeated dead-ends, confirmed
       wrong approaches that wasted significant time, or traps likely to recur.
       Do NOT persist routine errors, transient test failures, or trivial
       single-occurrence debugging steps.
     - Entries are human-readable markdown sections, not JSON blobs.
     - Do NOT include secrets, credentials, API keys, or PII in any field.
-->

<!-- Copy the template below for each new failure pattern entry. -->

<!--
### <short descriptive title>

- **date**: YYYY-MM-DD
  Guidance: ISO date when the pattern was first observed.
- **status**: active
  Guidance: Use "active" or "superseded". Only active entries are surfaced at startup.
- **project**: <repo or project identifier>
  Guidance: The repo where this pattern was observed.
- **task**: <originating spec or bug name>
  Guidance: For example, "002-prd-memory-enhancements" or "login-crash".
- **symptom**: <observable trigger condition>
  Guidance: What you see that indicates you are about to hit this trap.
- **failed_approach**: <what was tried and did not work>
  Guidance: Be specific; name the approach, not just "it did not work".
- **failure_reason**: <why it failed, if determinable>
  Guidance: Root cause or best understanding of why this approach fails.
- **successful_alternative**: <what worked instead, if known>
  Guidance: Leave blank if no alternative has been found yet.
- **classification**: <optional free-form value>
  Guidance: Forward-compatible with spec 001 finding taxonomy.
  Guidance: Known values may later include bad_design, intent_gap, patch, defer, or reject.
  Guidance: Leave blank or omit until a taxonomy is adopted.
- **superseded_by**: <task> @ YYYY-MM-DD, only when status is superseded
  Guidance: Reference the newer entry that replaces this one.
  Guidance: Only present when status is "superseded".
-->
