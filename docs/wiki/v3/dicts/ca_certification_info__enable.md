---
type: dict
title: ca_certification_info.enable
page_key: ca_certification_info__enable
belong: dicts
status: draft
anchors: [ca_certification_info.enable]
sources: ['database_profile:ca_certification_info.enable', 'database_schema:ca_certification_info.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [ca_certification_info]
---

# ca_certification_info.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `ca_certification_info.enable`，表页 [[tables/ca_certification_info]]。

## 取值

```ground:dict
dict: ca_certification_info__enable
fields: [ca_certification_info.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
