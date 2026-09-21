---
type: dict
title: funding_rule_front_cfg.key_type
page_key: funding_rule_front_cfg__key_type
belong: dicts
status: draft
anchors: [funding_rule_front_cfg.key_type]
sources: ['database_profile:funding_rule_front_cfg.key_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [funding_rule_front_cfg]
---

# funding_rule_front_cfg.key_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `funding_rule_front_cfg.key_type`，表页 [[tables/funding_rule_front_cfg]]。

## 取值

```ground:dict
dict: funding_rule_front_cfg__key_type
fields: [funding_rule_front_cfg.key_type]
values:
  FIELD_REQUIRED: {trust: proposed}
  FIELD_LENGTH_LIMIT: {trust: proposed}
  YEARS_CHECK: {trust: proposed}
  FILE_TYPE_LIMIT: {trust: proposed}
  FILE_NAME_SYMBOL: {trust: proposed}
  FILE_COUNT_LIMIT: {trust: proposed}
  FILE_SIZE_SINGLE_LIMIT: {trust: proposed}
  INVOICE_COUNT_LIMIT: {trust: proposed}
  FILE_SIZE_PACKAGE_LIMIT: {trust: proposed}
  DATE_CHECK_NATURAL: {trust: proposed}
  DATE_CHECK_WORKDAY: {trust: proposed}
  FILE_SIZE_TOTAL_LIMIT: {trust: proposed}
triage: keep
```
