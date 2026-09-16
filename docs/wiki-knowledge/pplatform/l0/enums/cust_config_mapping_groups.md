---
type: enum
title: cust_config_mapping_groups
page_key: cust_config_mapping_groups
belong: enums
status: draft
aliases: []
anchors:
- cust_config_mapping_groups
sources:
- database_profile:cust_config_mapping.groups
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_config_mapping_groups

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_config_mapping_groups
fields:
- cust_config_mapping.groups
values:
  ? ''
  : confidence: proposed
  BRANCH_COMPANY:
    confidence: proposed
  HEAD_COMPANY:
    confidence: proposed
ambiguous: false
```
