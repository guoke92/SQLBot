---
type: enum
title: funding_rule_front_cfg_key_type
page_key: funding_rule_front_cfg_key_type
belong: enums
status: draft
aliases: []
anchors:
- funding_rule_front_cfg_key_type
sources:
- database_profile:funding_rule_front_cfg.key_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# funding_rule_front_cfg_key_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: funding_rule_front_cfg_key_type
fields:
- funding_rule_front_cfg.key_type
values:
  FIELD_REQUIRED:
    confidence: proposed
  FIELD_LENGTH_LIMIT:
    confidence: proposed
  YEARS_CHECK:
    confidence: proposed
  FILE_TYPE_LIMIT:
    confidence: proposed
  FILE_NAME_SYMBOL:
    confidence: proposed
  FILE_COUNT_LIMIT:
    confidence: proposed
  FILE_SIZE_SINGLE_LIMIT:
    confidence: proposed
  INVOICE_COUNT_LIMIT:
    confidence: proposed
  FILE_SIZE_PACKAGE_LIMIT:
    confidence: proposed
  DATE_CHECK_NATURAL:
    confidence: proposed
  DATE_CHECK_WORKDAY:
    confidence: proposed
  FILE_SIZE_TOTAL_LIMIT:
    confidence: proposed
ambiguous: false
```
