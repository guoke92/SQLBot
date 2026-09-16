---
type: enum
title: cust_person_info_certification_type
page_key: cust_person_info_certification_type
belong: enums
status: draft
aliases: []
anchors:
- cust_person_info_certification_type
sources:
- database_profile:cust_person_info.certification_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_person_info_certification_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_person_info_certification_type
fields:
- cust_person_info.certification_type
values:
  CRET_ID:
    confidence: proposed
  CREDENTIALS_ID:
    confidence: proposed
  CERT_RESIDENT_PERMIT:
    confidence: proposed
  CERT_PASSPORT:
    confidence: proposed
  CERT_GREEN_CARD:
    confidence: proposed
  CERT_TAIWAN:
    confidence: proposed
  CERT_MAINLAND_PASS:
    confidence: proposed
  CERT_HK_AND_MACAU_PASS:
    confidence: proposed
  CRET_ID_HK:
    confidence: proposed
ambiguous: false
```
