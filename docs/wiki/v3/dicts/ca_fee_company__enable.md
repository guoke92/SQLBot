---
type: dict
title: ca_fee_company.enable
page_key: ca_fee_company__enable
belong: dicts
status: draft
anchors: [ca_fee_company.enable]
sources: ['database_profile:ca_fee_company.enable', 'database_schema:ca_fee_company.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [ca_fee_company]
---

# ca_fee_company.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `ca_fee_company.enable`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__enable
fields: [ca_fee_company.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
