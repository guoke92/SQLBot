---
type: dict
title: cust_certification_info.enable
page_key: cust_certification_info__enable
belong: dicts
status: draft
anchors: [cust_certification_info.enable]
sources: ['database_profile:cust_certification_info.enable', 'database_schema:cust_certification_info.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_certification_info]
---

# cust_certification_info.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_certification_info.enable`，表页 [[tables/cust_certification_info]]。

## 取值

```ground:dict
dict: cust_certification_info__enable
fields: [cust_certification_info.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
