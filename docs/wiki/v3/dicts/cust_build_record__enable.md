---
type: dict
title: cust_build_record.enable
page_key: cust_build_record__enable
belong: dicts
status: draft
anchors: [cust_build_record.enable]
sources: ['database_profile:cust_build_record.enable', 'database_schema:cust_build_record.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_build_record]
---

# cust_build_record.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_build_record.enable`，表页 [[tables/cust_build_record]]。

## 取值

```ground:dict
dict: cust_build_record__enable
fields: [cust_build_record.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
