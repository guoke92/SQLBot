---
type: dict
title: cust_change_cfg.enable
page_key: cust_change_cfg__enable
belong: dicts
status: draft
anchors: [cust_change_cfg.enable]
sources: ['database_profile:cust_change_cfg.enable', 'database_schema:cust_change_cfg.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_change_cfg]
---

# cust_change_cfg.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_change_cfg.enable`，表页 [[tables/cust_change_cfg]]。

## 取值

```ground:dict
dict: cust_change_cfg__enable
fields: [cust_change_cfg.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
