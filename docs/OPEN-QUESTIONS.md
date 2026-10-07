# Open questions from scenario authoring

Collected from each scenario file's `openQuestions`. Resolve with the Payroc API / platform owners, then update the scenario JSON and remove the entry.

**Highest priority:** which request field is indexed in Splunk (drives `tagField` for every endpoint) and the 24-character limit on Apple Pay / Worldnet order ids (Test Tag budget).


## Authentication

- Worldnet auth hash scenarios not authored: belongs to Worldnet hosted pages and worldnet-reference was not consulted
- AUTH-03/05: scope-limited keys and forced expiry in UAT not documented

## Merchant boarding

- BRD-05: Source of the HATEOAS sign link at submission time is not fully documented
- BRD-07/BRD-08: UAT pricing intent ids and approved fee values come from Payroc
- BRD-12: Whether UAT permits duplicate taxId testing is unconfirmed

## Payroc Cloud card-present

- CP-02: UAT decline trigger amounts/cards not documented in skill
- CP-05: How to simulate device offline/timeout in UAT (simulator?) not documented
- CP-07: Source of a settled UAT payment for referenced refund not documented
- CP-12: UAT surcharge setup not documented
- CP-13: closed-loop test cards not documented
- Cloud error shape is assumed to match the standard envelope and is unverified on Cloud (per skill)
- Prefix CP assumed for Cloud (authoring guide lists no dedicated Cloud prefix)

## 8.2e Direct API Payments

- CNP-02/CNP-14/CNP-15/CNP-16 and 3DS-01..03: UAT decline, AVS/CVV, partial approval and 3DS outcome trigger values are not documented in the source skills
- All Payroc scenarios: UAT test card numbers and ACH/PAD test accounts not documented in the source skills
- Test Tag length (about 30 chars) exceeds order.orderId 24-char limit documented for Apple Pay payments and Worldnet ORDERID; decide whether the tag goes in customFields or description
- CNP-05/CNP-06: capture and adjust request body shapes not fully specified in the skill
- CNP-14/CNP-18: billing address and tax object field names not specified
- CNP-19: EBT payment request shape not covered by source skills
- CNP-11: exact status for cumulative over-refund not stated
- WN-02: whether totalAmount is decimal or minor units; WN-03: decline status code; WN-06: refund body; WN-08/WN-09: sandbox test data; production REST base URL not stated
- ACH-08: ACH re-presentment limited and PAD unavailable in UAT
- Worldnet idempotency: no Idempotency-Key documented

## Terminal orders and equipment

- EQ-06: processing-terminal reads unverified/unavailable in UAT
- Payment intent (who pays) scenarios omitted; add if SD requires

## Error handling

- ERR-06: 429 not documented in sourced skills; rate limits unknown
- ERR-07: how to induce timeouts in UAT left to partner

## Funding

- FND-07: How to hold a UAT instruction past accepted not documented
- FND-01: UAT KYC simulation requires Payroc enablement

## Gateway configuration

- Worldnet self-care configuration not documented in sourced skills; no Worldnet scenarios authored
- Gateway_Payroc template name taken from legacy guide; confirm against skill enum
- Gateway-level settings beyond solutionSetup unknown

## Go-live cutover checklist

- GL-08: Payroc policy on production penny/first live transaction unknown
- GL prefix not in authoring guide prefix list; confirm
- Production approval/sign-off process unknown

## 8.2b Hosted Fields

- HF-02..HF-06: UAT test cards and decline/3DS triggers not documented in source skills
- HF-01: session success status code not stated
- HF-03: status code for reused token not pinned (400/422)
- Worldnet hosted-fields equivalent: none documented in worldnet-reference (GoChip excluded)

## 8.2c Hosted Payment Pages

- HPP-01..06: hash recipe, AMOUNT/DATETIME formats and full RESPONSECODE set live in Payroc skill references not reproduced here; certifier should pull exact values
- HPP-02: UAT decline trigger not documented
- WN-21..29: WN id range chosen to avoid direct-api WN-01..11; reassign if the catalogue collides
- WN HPP production URLs and validation retry policy not documented
- Test Tag length vs ORDERID 24-char limit

## 8.2d Payment Links

- PL-01: exact position of charge/order fields and required set not fully shown in skill
- Worldnet: no payment-link API in worldnet-reference (Pay Link/eInvoice are Selfcare features only; XML pages not in snapshot)

## 8.2g Recurring and Tokens

- Worldnet equivalents (credentials, paymentPlans, subscriptions endpoints) not authored in this file
- Subscription failure/suspension (gateway) test triggers not documented
- REC-06 MIT schema details

## Reporting and event notifications

- EV-05: retry interval/backoff after 5 attempts not documented
- EV-03: no HMAC signature documented; only Payroc-Secret header
- RPT-*: UAT data seeding for settlement/disputes not documented

## Security attestations

- Specific Payroc security/PCI requirements to confirm with Payroc security

## 8.2h Verification and Lookups

- VER-01/04: UAT test accounts and failing trigger not documented
- VER-03: card details shape for EBT chip/keyed entry
- Worldnet equivalents (customer/cards/verify, lookup, balance, accounts/verify) not authored

## 8.2f Digital Wallets

- AP-02/GP-01: orderId 1-24 chars vs Test Tag length; choose a different tagField
- Wallet test cards and decline triggers not documented
- Worldnet wallet equivalents (applePaySessions, DIGITAL_WALLET payload; Elavon only) not authored here; see WN-28 for HPP
