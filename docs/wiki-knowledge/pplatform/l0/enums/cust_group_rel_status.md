---
type: enum
title: cust_group_rel_status
page_key: cust_group_rel_status
belong: enums
status: draft
aliases: []
anchors:
- cust_group_rel_status
sources:
- database_profile:cust_group_rel.status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_group_rel_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_group_rel_status
fields:
- cust_group_rel.status
values:
  EFFECTIVE:
    confidence: proposed
  INEFFECTIVE:
    confidence: proposed
  REJECTED:
    confidence: proposed
ambiguous: false
```
