---
type: dict
title: cust_company_info.audit_back_flag
page_key: cust_company_info__audit_back_flag
belong: dicts
status: draft
anchors: [cust_company_info.audit_back_flag]
sources: ['database_profile:cust_company_info.audit_back_flag', 'database_schema:cust_company_info.audit_back_flag']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.audit_back_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_company_info.audit_back_flag`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__audit_back_flag
fields: [cust_company_info.audit_back_flag]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是}
triage: keep
```
