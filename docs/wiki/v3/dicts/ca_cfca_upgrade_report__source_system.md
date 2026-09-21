---
type: dict
title: ca_cfca_upgrade_report.source_system
page_key: ca_cfca_upgrade_report__source_system
belong: dicts
status: draft
anchors: [ca_cfca_upgrade_report.source_system]
sources: ['database_profile:ca_cfca_upgrade_report.source_system']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_cfca_upgrade_report]
---

# ca_cfca_upgrade_report.source_system

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `ca_cfca_upgrade_report.source_system`，表页 [[tables/ca_cfca_upgrade_report]]。

## 取值

```ground:dict
dict: ca_cfca_upgrade_report__source_system
fields: [ca_cfca_upgrade_report.source_system]
values:
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  国内信用证: {trust: proposed}
  ORDER: {trust: proposed}
triage: hold
needs_review: true
```
