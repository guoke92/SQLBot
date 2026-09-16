---
type: enum
title: cust_oper_change_record_change_type
page_key: cust_oper_change_record_change_type
belong: enums
status: draft
aliases: []
anchors:
- cust_oper_change_record_change_type
sources:
- database_profile:cust_oper_change_record.change_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_oper_change_record_change_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_oper_change_record_change_type
fields:
- cust_oper_change_record.change_type
values:
  BATCH:
    confidence: proposed
  ASSET_AUDIT_SYNC:
    confidence: proposed
  CUST_CHANGE_CALLBACK:
    confidence: proposed
  MANUAL:
    confidence: proposed
ambiguous: false
```
