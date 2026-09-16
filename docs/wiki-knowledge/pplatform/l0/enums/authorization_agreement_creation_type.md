---
type: enum
title: authorization_agreement_creation_type
page_key: authorization_agreement_creation_type
belong: enums
status: draft
aliases: []
anchors:
- authorization_agreement_creation_type
sources:
- database_profile:authorization_agreement.creation_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# authorization_agreement_creation_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: authorization_agreement_creation_type
fields:
- authorization_agreement.creation_type
values:
  CUST_BUILD_INIT:
    confidence: proposed
  AUTO:
    confidence: proposed
  COMPANY_MANAGER_CHANGE_CODE:
    confidence: proposed
ambiguous: false
```
