---
type: dict
title: cust_company_info.cust_source
page_key: cust_company_info__cust_source
belong: dicts
status: draft
anchors: [cust_company_info.cust_source]
sources: ['database_profile:cust_company_info.cust_source', 'database_schema:cust_company_info.cust_source',
  'code_path:CustSourceEnum.java:21', 'code_path:CustSourceEnum.java:20', 'code_path:CustSourceEnum.java:19']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cust_source

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_company_info.cust_source`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cust_source
fields: [cust_company_info.cust_source]
values:
  PPLATFORM: {trust: confirmed, label: 产融自建企业, evidence: 'code_path:CustSourceEnum.java:21'}
  MIGRATORY: {trust: confirmed, label: 存量迁移企业, evidence: 'code_path:CustSourceEnum.java:20'}
  PLATFORM_PUSH: {trust: confirmed, label: 运营中台推送, evidence: 'code_path:CustSourceEnum.java:19'}
  PLATFORM: {trust: proposed}
triage: keep
```
