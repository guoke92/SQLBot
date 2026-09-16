---
type: enum
title: funding_rule_info_rule_status
page_key: funding_rule_info_rule_status
belong: enums
status: draft
aliases: []
anchors:
- funding_rule_info_rule_status
sources:
- database_profile:funding_rule_info.rule_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# funding_rule_info_rule_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: funding_rule_info_rule_status
fields:
- funding_rule_info.rule_status
values:
  PENDING:
    confidence: proposed
  ACTIVE:
    confidence: proposed
  INACTIVE:
    confidence: proposed
ambiguous: false
```
