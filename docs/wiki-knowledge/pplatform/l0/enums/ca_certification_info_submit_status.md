---
type: enum
title: ca_certification_info_submit_status
page_key: ca_certification_info_submit_status
belong: enums
status: draft
aliases: []
anchors:
- ca_certification_info_submit_status
sources:
- database_profile:ca_certification_info.submit_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# ca_certification_info_submit_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: ca_certification_info_submit_status
fields:
- ca_certification_info.submit_status
values:
  SUCCESS:
    confidence: proposed
  PENDING:
    confidence: proposed
  FAIL:
    confidence: proposed
ambiguous: false
```
