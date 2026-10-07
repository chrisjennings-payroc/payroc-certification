# Payroc Certification Script toolkit

Builds partner **Certification Scripts**: the UAT test plan a partner runs (and Payroc verifies) before going to production. It is
the companion to the [Payroc Solution Design toolkit](https://github.com/chrisjennings-payroc/payroc-solution-design): the SD says how the partner will use
Payroc, the certification script is tailored from the SD `.md` to test exactly that.

Covers every Payroc API workflow (boarding, hosted fields, HPP, payment links, Cloud card-present, direct API, wallets, recurring/tokens, verification,
equipment, gateway, funding, reporting/events), cross-cutting auth/errors/security/go-live, plus the **Worldnet direct API and Worldnet hosted pages**.
Worldnet GoChip SDK and eComm plugins are out of scope.

## Install (Payroc SEs and certifiers)

```text
/plugin marketplace add <github-org>/payroc-certification
/plugin install payroc-certification@payroc-certification-toolkit
```
Local checkout: `/plugin marketplace add ./` from this folder. See [docs/SECURITY.md](docs/SECURITY.md) if your organisation restricts marketplaces.

## Use

| Command | What it does |
|---|---|
| `/payroc-certification:cert-new <sd.md> [folder]` | Tailor the catalogue to the SD -> `<Partner>-Certification-Script.html` + `.md` |
| `/payroc-certification:cert-import <script.html> <sd.md>` | Re-tailor after the SD changed (done in-browser, keeps results) |
| `/payroc-certification:cert-review <script.html>` | Consistency, blockers without reasons, missing evidence, secrets scan, Splunk tag list |

Without Claude (partners, or anyone): open the generated `.html` in Chrome/Edge. **Import SD (.md)** tailors the script in the browser; **Autosave .html / .md / .pdf**
write all three files as you work. Hand the `.md` to any AI assistant to help fill in evidence, then **Import results** to bring it back.

## How the flow works
1. SE finishes the SD and shares its `.md`. `cert-new` produces the script (also: `--template-only` for the full catalogue).
2. Partner runs each scenario in UAT, sending the scenario's **Test Tag** in the field shown, pastes the response, and sets Pass / Fail / **Blocked** / **Needs follow-up**.
3. Payroc reviewer switches to *reviewer view*, searches each Test Tag in Splunk (log lookup panel) and ticks **Verified in logs**. A scenario is certified when it is passed and verified.

Scenario content lives in `payroc-certification/skills/create-certification-script/scenarios/*.json`; see [docs/SCENARIO-AUTHORING.md](docs/SCENARIO-AUTHORING.md) and
[docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) (items to confirm with API owners before the first pilot). Tests: [docs/TESTING.md](docs/TESTING.md).

## Maintainers
Branch from `main` (`feature/...`, `fix/...`), update `CHANGELOG.md`, bump the version in both manifests (`.claude-plugin/marketplace.json` and `payroc-certification/.claude-plugin/plugin.json`), open a PR, tag after merge.
