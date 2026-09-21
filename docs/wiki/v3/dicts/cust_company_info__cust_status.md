---
type: dict
title: cust_company_info.cust_status
page_key: cust_company_info__cust_status
belong: dicts
status: draft
anchors: [cust_company_info.cust_status]
sources: ['database_profile:cust_company_info.cust_status', 'database_schema:cust_company_info.cust_status',
  'code_path:CustStatusEnum.java:20', 'code_path:CustStatusEnum.java:19', 'code_path:CustStatusEnum.java:24',
  'code_path:CustStatusEnum.java:22', 'code_path:CustStatusEnum.java:23', 'code_path:CustStatusEnum.java:21']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cust_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_company_info.cust_status`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cust_status
fields: [cust_company_info.cust_status]
values:
  EFFECT: {trust: confirmed, label: 生效, evidence: 'code_path:CustStatusEnum.java:20'}
  ADD: {trust: confirmed, label: 新增, evidence: 'code_path:CustStatusEnum.java:19'}
  CHANGE: {trust: confirmed, label: 变更, evidence: 'code_path:CustStatusEnum.java:24'}
  WRITEOFF: {trust: confirmed, label: 注销, evidence: 'code_path:CustStatusEnum.java:22'}
  FREEZE: {trust: confirmed, label: 冻结, evidence: 'code_path:CustStatusEnum.java:23'}
  FAILURE: {trust: confirmed, label: 失效, evidence: 'code_path:CustStatusEnum.java:21'}
triage: keep
```
