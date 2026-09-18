---
type: dict
title: cust_company_info.data_type
page_key: cust_company_info__data_type
belong: dicts
status: draft
anchors: [cust_company_info.data_type]
sources: ['database_profile:cust_company_info.data_type', 'database_schema:cust_company_info.data_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.data_type

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_company_info.data_type`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__data_type
fields: [cust_company_info.data_type]
values:
  '1': {trust: proposed, label: 主数据, evidence: 'database_schema:cust_company_info.data_type'}
  '0': {trust: proposed, label: 记录数据, evidence: 'database_schema:cust_company_info.data_type'}
  '2': {trust: proposed}
triage: keep
```
