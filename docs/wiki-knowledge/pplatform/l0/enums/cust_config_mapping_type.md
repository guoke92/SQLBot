---
type: enum
title: cust_config_mapping_type
page_key: cust_config_mapping_type
belong: enums
status: draft
aliases: []
anchors:
- cust_config_mapping_type
sources:
- database_profile:cust_config_mapping.type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_config_mapping_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_config_mapping_type
fields:
- cust_config_mapping.type
values:
  COMPANY_TYPE_MAPPING:
    confidence: proposed
  COMPANY_MEDIA:
    confidence: proposed
  CHANGE_ITEM:
    confidence: proposed
ambiguous: false
```
