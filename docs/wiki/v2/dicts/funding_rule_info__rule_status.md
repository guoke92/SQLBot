---
type: dict
title: funding_rule_info.rule_status
page_key: funding_rule_info__rule_status
belong: dicts
status: draft
anchors: [funding_rule_info.rule_status]
sources: ['database_profile:funding_rule_info.rule_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [funding_rule_info]
---

# funding_rule_info.rule_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `funding_rule_info.rule_status`，表页 [[tables/funding_rule_info]]。

## 取值

```ground:dict
dict: funding_rule_info__rule_status
fields: [funding_rule_info.rule_status]
values:
  PENDING: {trust: proposed}
  ACTIVE: {trust: proposed}
  INACTIVE: {trust: proposed}
triage: keep
```
