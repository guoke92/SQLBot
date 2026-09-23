---
type: dict
title: ca_cfca_upgrade_report.enable
page_key: ca_cfca_upgrade_report__enable
belong: dicts
status: draft
anchors: [ca_cfca_upgrade_report.enable]
sources: ['database_profile:ca_cfca_upgrade_report.enable', 'database_schema:ca_cfca_upgrade_report.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [ca_cfca_upgrade_report]
---

# ca_cfca_upgrade_report.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `ca_cfca_upgrade_report.enable`，表页 [[tables/ca_cfca_upgrade_report]]。

## 取值

```ground:dict
dict: ca_cfca_upgrade_report__enable
fields: [ca_cfca_upgrade_report.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
