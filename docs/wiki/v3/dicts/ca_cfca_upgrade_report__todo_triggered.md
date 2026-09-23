---
type: dict
title: ca_cfca_upgrade_report.todo_triggered
page_key: ca_cfca_upgrade_report__todo_triggered
belong: dicts
status: draft
anchors:
- ca_cfca_upgrade_report.todo_triggered
sources:
- database_profile:ca_cfca_upgrade_report.todo_triggered
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- ca_cfca_upgrade_report
---
# ca_cfca_upgrade_report.todo_triggered

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `ca_cfca_upgrade_report.todo_triggered`，表页 [[tables/ca_cfca_upgrade_report]]。

## 取值

```ground:dict
dict: ca_cfca_upgrade_report__todo_triggered
fields:
- ca_cfca_upgrade_report.todo_triggered
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
