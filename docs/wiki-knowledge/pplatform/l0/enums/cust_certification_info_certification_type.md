---
type: enum
title: cust_certification_info_certification_type
page_key: cust_certification_info_certification_type
belong: enums
status: draft
aliases: []
anchors:
- cust_certification_info_certification_type
sources:
- database_profile:cust_certification_info.certification_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_certification_info_certification_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_certification_info_certification_type
fields:
- cust_certification_info.certification_type
values:
  FACE_VERIFY:
    confidence: proposed
  AUTH_THREE_ELEMENTS:
    confidence: proposed
  LEGAL_REAL_NAME:
    confidence: proposed
  LEGAL_THREE_ELEMENTS:
    confidence: proposed
  COMPANY_TWO_ELEMENTS:
    confidence: proposed
  LEGAL_OCR:
    confidence: proposed
  AUTH_MEDIA_OCR:
    confidence: proposed
ambiguous: false
```
