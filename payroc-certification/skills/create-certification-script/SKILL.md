---
name: create-certification-script
description: Builds a Payroc partner Certification Script - the branded, browser-editable HTML (plus a .md twin; PDF via Download copies) that lists the UAT test scenarios a partner must run before production. Use when a Payroc Sales Engineer or certifier wants to create, tailor, import results into, or review a certification script, UAT test plan or go-live checklist for an ISV / PayFac / referral partner, especially from a Solution Design .md. Covers all Payroc APIs plus the Worldnet direct API and Worldnet hosted pages. Not for Worldnet GoChip SDK or eComm plugins.
version: "0.1.0"
category: sales-engineering
status: draft
---

# Create a Certification Script

The certification script is the second half of the Solution Design (SD) flow: the SD records *how the partner intends to use
Payroc*, the certification script lists *the tests that prove it* in UAT.

## What it produces
`{Partner}-Certification-Script.html` (self-contained, offline, editable, autosaves to .html/.md in Chrome/Edge) and a
`.md` twin that any AI tool can read and help fill in. Scenarios, steps, expected results and evidence fields come from
`scenarios/*.json` (the single source of truth, 15 section files).

## Steps
1. Get the SD `.md` (the twin of the SD HTML). If only the HTML exists, ask the SE to enable `.md` autosave first.
2. `python3 scripts/parse-sd.py <sd.md>` to preview scope, then `python3 scripts/build-cert.py <sd.md> --out <dir>`.
   Use `--template-only` for the full catalogue with no SD.
3. `python3 scripts/review-cert.py <script.html>` before sharing.
4. Remind the SE: open in Chrome/Edge, click Autosave .html and .md.

## Tailoring rules (scripts/certlib.py mirrors the `// <tailor>` block in template.html; tests compare them)
- Cross-cutting sections (auth, errors, security, go-live) are always in.
- Workflow sections follow the SD's `in_scope` / `workflows_in_scope`; the SD's `platform` (payroc/worldnet/both) selects scenario variants.
- `conditional` scenarios appear only if one of their `appliesWhen` keywords occurs in the SD section's checked items or text
  (unchecked `- [ ]` lines and `[TODO:` lines never trigger). A `required` scenario whose primary endpoint is marked `[Optional]` in the SD is demoted to `recommended`.
- Unresolved SD fields become "Needs follow-up" items. The SD's Worldnet SDK/plugin section is noted as out of certification scope.

## Test identification
Test Tag = `{CertRunID}-{ScenarioID}-{attempt}` (<= 24 chars). The partner sends it in the request field shown for each endpoint (`tagField`) so the
certification team can search it in Splunk. Confirm the indexed field with the platform team (see `docs/SCENARIO-AUTHORING.md`).

## Never
Invent endpoints, amounts, test cards or response codes: take them from the matching Payroc skill or `worldnet-reference`, or record an `openQuestions` entry.
Put real card numbers, API keys or secrets in a script.
