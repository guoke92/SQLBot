---
type: enum
title: cust_role_info_status
page_key: cust_role_info_status
belong: enums
status: draft
aliases: []
anchors:
- cust_role_info_status
sources:
- database_profile:cust_role_info.status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_role_info_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_role_info_status
fields:
- cust_role_info.status
values:
  ADD:
    confidence: proposed
  EFFECT:
    confidence: proposed
  WRITEOFF:
    confidence: proposed
  FREEZE:
    confidence: proposed
ambiguous: false
```
