# Scenario authoring guide

Scenarios are the source of truth for the certification script. One JSON file per Solution Design (SD) section id lives in
`payroc-certification/skills/create-certification-script/scenarios/<section>.json`. The builder (`scripts/build-cert.py`) and the
in-browser SD import both read these files.

## Principles

- This is a **certification** of Payroc's API contract, not a QA guide for the partner's application. Each scenario is one
  request -> expected response/state that a Payroc certifier can verify in logs. Keep it lean: 3-12 scenarios per section.
- Never invent endpoints, fields, amounts, test cards, response codes or limits. Take them from the matching Payroc skill
  (invoke it) or, for Worldnet, from the `worldnet-reference` skill files. If a trigger value (decline amount, test card) is
  not documented, write `"testData": "Use the UAT trigger documented at docs.payroc.com/... (confirm with Payroc)"` and add the
  scenario id to the file's `openQuestions` list.
- Out of scope (do not write scenarios for): Worldnet GoChip SDK, eComm/shopping-cart plugins, POS plugins.
- Tiers: `required` (gate to production), `conditional` (only when the SD indicates the feature), `recommended`.

## File shape

```json
{
  "section": "direct-api",
  "label": "8.2e Direct API Payments",
  "sourceSkills": ["run-a-card-sale"],
  "openQuestions": ["CNP-03: AVS trigger values not documented"],
  "scenarios": [
    {
      "id": "CNP-01",
      "title": "Card sale approved",
      "tier": "required",
      "kind": "happy",
      "platform": "payroc",
      "appliesWhen": [],
      "objective": "One sentence: what Payroc is verifying.",
      "steps": ["Ordered, imperative steps the partner performs in UAT."],
      "expected": "What the response/state must be, incl. HTTP status and key fields.",
      "expectedStatus": 201,
      "endpoints": [{"method": "POST", "path": "/v1/payments", "tagField": "order.orderId"}],
      "testData": "Optional: documented test card/amount or null",
      "requestExample": {"any": "valid JSON from the skill"},
      "evidence": ["paymentId", "HTTP status", "Idempotency-Key"],
      "pitfalls": "Optional common mistake to watch for"
    }
  ]
}
```

Field rules:
- `id`: `<PREFIX>-<NN>`, unique across the whole catalogue, never reused. Prefixes: AUTH, ERR, CNP, 3DS, HF, HPP, PL, TOK, REC,
  AP, GP, CP, ACH, VER, BRD, EQ, GW, EV, FND, RPT, SEC, WN.
- `platform`: `payroc`, `worldnet` or `both`. Worldnet scenarios cover the Worldnet direct API and Worldnet hosted pages only.
- `appliesWhen`: list of lowercase keywords. A `conditional` scenario is included when ANY keyword appears (case-insensitive
  substring) in the SD section's checked decisions, in-scope endpoint rows, or free text. `required`/`recommended` scenarios
  use `[]` and are included whenever the section is in scope.
- `tagField`: the request field the partner must populate with the Test Tag so the run can be found in Splunk. Default
  proposal: the merchant-supplied order/reference field of that endpoint; if none exists use `Idempotency-Key` (suffix).
- `requestExample`: sanitized, never real card numbers except documented UAT test cards; use `{{TEST_TAG}}` where the tag goes
  and `{{IDEMPOTENCY_KEY}}` for the key.
- `evidence`: the response fields the certifier needs to find the call (resource ids, status).

## Tags

Test Tag = `{IntegrationProjectNumber}-{ScenarioID}-{attempt}`, e.g. `12345-CNP-01-1`. Keep the whole tag <= 24 characters: Apple Pay and Worldnet order ids are limited to 24.
