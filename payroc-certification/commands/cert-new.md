---
description: Build a tailored Certification Script (HTML + .md) from a partner's Solution Design .md
argument-hint: <path to Partner-Solution-Design.md> [output folder]
allowed-tools: Bash(python3:*), Read, Write, Glob, Grep
---

Create a Certification Script from the Solution Design at: $ARGUMENTS

1. Confirm the first argument is a Solution Design `.md` (it has `<!-- sd:section=... -->` markers). If only the
   `.html` was given, use the `.md` twin next to it; if no twin exists, stop and ask the SE to enable `.md` autosave.
2. Preview the scope: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/create-certification-script/scripts/parse-sd.py" <sd.md>`.
   Show the SE which sections are in/out, which platform (Payroc / Worldnet) each uses, and any SD follow-ups
   (unresolved fields). Mention that Worldnet GoChip SDK and eComm plugins are intentionally not covered.
3. Build: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/create-certification-script/scripts/build-cert.py" <sd.md> --out <folder>`
   (default output: the folder containing the SD). Report the two files written and the Cert Run ID.
4. Run `review-cert.py` on the new `.html` and report anything it flags.
5. Tell the SE the next steps: open the `.html` in Chrome/Edge, enable autosave for `.html` and `.md`, then share
   the files with the partner. Do not edit scenario content here; see `docs/SCENARIO-AUTHORING.md` for catalogue changes.
