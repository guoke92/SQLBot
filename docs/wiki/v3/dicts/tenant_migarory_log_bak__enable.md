---
type: dict
title: tenant_migarory_log_bak.enable
page_key: tenant_migarory_log_bak__enable
belong: dicts
status: draft
anchors: [tenant_migarory_log_bak.enable]
sources: ['database_profile:tenant_migarory_log_bak.enable', 'database_schema:tenant_migarory_log_bak.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_migarory_log_bak]
---

# tenant_migarory_log_bak.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_migarory_log_bak.enable`，表页 [[tables/tenant_migarory_log_bak]]。

## 取值

```ground:dict
dict: tenant_migarory_log_bak__enable
fields: [tenant_migarory_log_bak.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
