---
type: enum
title: funding_rule_detail_rule_layer
page_key: funding_rule_detail_rule_layer
belong: enums
status: draft
aliases: []
anchors:
- funding_rule_detail_rule_layer
sources:
- database_profile:funding_rule_detail.rule_layer
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# funding_rule_detail_rule_layer

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: funding_rule_detail_rule_layer
fields:
- funding_rule_detail.rule_layer
values:
  FINANCING:
    confidence: proposed
  UNDERLYING:
    confidence: proposed
  OTHER:
    confidence: proposed
ambiguous: false
```
