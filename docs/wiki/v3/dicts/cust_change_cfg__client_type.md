---
type: dict
title: cust_change_cfg.client_type
page_key: cust_change_cfg__client_type
belong: dicts
status: draft
anchors: [cust_change_cfg.client_type]
sources: ['database_profile:cust_change_cfg.client_type', 'database_schema:cust_change_cfg.client_type',
  'code_path:ClientTypeConstants.java:6', 'code_path:ClientTypeConstants.java:9']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_change_cfg]
---

# cust_change_cfg.client_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_change_cfg.client_type`，表页 [[tables/cust_change_cfg]]。

## 取值

```ground:dict
dict: cust_change_cfg__client_type
fields: [cust_change_cfg.client_type]
values:
  AGW: {trust: confirmed, label: 内管, evidence: 'code_path:ClientTypeConstants.java:6'}
  ACCOUNT_PRODUCT: {trust: confirmed, label: 客户端, evidence: 'code_path:ClientTypeConstants.java:9'}
triage: keep
```
