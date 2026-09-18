---
type: dict
title: cust_change_cfg.cust_type
page_key: cust_change_cfg__cust_type
belong: dicts
status: draft
anchors: [cust_change_cfg.cust_type]
sources: ['database_profile:cust_change_cfg.cust_type', 'database_schema:cust_change_cfg.cust_type',
  'code_path:CustTypeEnum.java:18', 'code_path:CustTypeEnum.java:17', 'code_path:CustTypeEnum.java:19']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_change_cfg]
---

# cust_change_cfg.cust_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_change_cfg.cust_type`，表页 [[tables/cust_change_cfg]]。

## 取值

```ground:dict
dict: cust_change_cfg__cust_type
fields: [cust_change_cfg.cust_type]
values:
  '2': {trust: confirmed, label: 企业客户, evidence: 'code_path:CustTypeEnum.java:18'}
  '1': {trust: confirmed, label: 个人客户, evidence: 'code_path:CustTypeEnum.java:17'}
  '3': {trust: confirmed, label: 运营方企业客户, evidence: 'code_path:CustTypeEnum.java:19'}
triage: keep
```
