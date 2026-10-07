---
description: Re-tailor an existing Certification Script after the Solution Design changed (keeps recorded results)
argument-hint: <path to existing Certification Script .html> <path to updated Solution Design .md>
allowed-tools: Bash(python3:*), Read, Glob
---

The SD changed after the Certification Script was generated: $ARGUMENTS

Re-tailoring keeps every recorded result, so do it in the browser rather than rebuilding:
1. Tell the SE to open the existing Certification Script in Chrome/Edge and click **Import SD (.md)**, choosing the updated SD.
   Scenarios that already have results stay in the script even if the new SD no longer calls for them.
2. If the script cannot be opened in a browser, run `parse-sd.py` on the updated SD
   (`python3 "${CLAUDE_PLUGIN_ROOT}/skills/create-certification-script/scripts/parse-sd.py" <sd.md>`) and summarise
   what changed in scope versus the old script's `scenarios_total` and sections.
3. Do not overwrite the existing files.
