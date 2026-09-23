---
type: dict
title: cust_company_info.cert_no_flag
page_key: cust_company_info__cert_no_flag
belong: dicts
status: draft
anchors: [cust_company_info.cert_no_flag]
sources: ['database_profile:cust_company_info.cert_no_flag', 'database_schema:cust_company_info.cert_no_flag']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cert_no_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_company_info.cert_no_flag`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cert_no_flag
fields: [cust_company_info.cert_no_flag]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
