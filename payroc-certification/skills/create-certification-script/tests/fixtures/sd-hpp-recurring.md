---
document: payroc-solution-design
template_version: "0.2.0"
partner: "Acme Coffee Software"
prepared_by: "Jordan SE"
partner_contact: "dev@acme.example"
status: "Draft"
target_go_live: "2026-12-01"
workflows_in_scope: ["boarding","hpp","recurring","reporting"]
platforms: {"boarding":"payroc","hpp":"payroc","recurring":"payroc","reporting":"payroc"}
unresolved_fields: 1
---

# Acme Coffee Software — Solution Design

<!-- sd:section=boarding -->
## 8.1 Boarding & Merchant Management

- in_scope: yes
- platform: payroc

- [x] Direct-link signature
- [ ] Embedded signature

| Method | Endpoint | Purpose | Status |
|---|---|---|---|
| POST | `/merchant-platforms` | Create merchant | [Required] |
| POST | `/processing-accounts/{processingAccountId}/attachments` | Upload docs | [Optional] |

<!-- sd:section=hpp -->
## 8.2b Hosted Payment Pages

- in_scope: yes
- platform: payroc

- [x] Pre-authorization and capture
- [ ] Save card

<!-- sd:section=recurring -->
## 8.4 Recurring Billing & Tokenization

- in_scope: yes
- platform: payroc

- [x] Payment plans and subscriptions
- Billing owner: [TODO: who owns retries?]

<!-- sd:section=reporting -->
## 8.9 Reporting & Notifications

- in_scope: yes
- platform: payroc

- [x] Event subscriptions (webhooks)

<!-- sd:section=cloud -->
## 8.2d Payroc Cloud

- in_scope: no
- platform: payroc
