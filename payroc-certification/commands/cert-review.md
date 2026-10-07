---
description: Pre-share / pre-certification review of a Certification Script (consistency, reasons on blockers, evidence, secrets)
argument-hint: <path to Partner-Certification-Script.html> [updated .md from partner]
allowed-tools: Bash(python3:*), Read, Glob, Grep
---

Review the Certification Script at: $ARGUMENTS

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/skills/create-certification-script/scripts/review-cert.py" <file.html>`
   (it reads the `.md` twin next to it, or the one given after `--md`) and report every problem.
2. Read the `.md`. Summarise: counts by status, every `blocked` / `follow_up` item with its reason and owner, scenarios marked
   `pass` without `http_status`, `timestamp_utc` or `resource_id` evidence, and `required` scenarios not yet run.
3. For the Payroc reviewer: list the `test_tag` of every scenario with a recorded run and not `verified_in_logs`, so they
   can be searched in Splunk. Do not state that a run exists in Splunk; only the reviewer can verify that.
4. Offer fixes; do not edit the files without confirmation.
