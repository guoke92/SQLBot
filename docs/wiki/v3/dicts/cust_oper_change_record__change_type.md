---
type: dict
title: cust_oper_change_record.change_type
page_key: cust_oper_change_record__change_type
belong: dicts
status: draft
anchors: [cust_oper_change_record.change_type]
sources: ['database_profile:cust_oper_change_record.change_type', 'database_schema:cust_oper_change_record.change_type',
  'code_path:OperChangeRecordApplication.java:28', 'code_path:OperChangeRecordApplication.java:31',
  'code_path:OperChangeRecordApplication.java:32', 'code_path:OperChangeRecordApplication.java:27',
  'code_path:OperChangeRecordApplication.java:29', 'code_path:OperChangeRecordApplication.java:30']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_oper_change_record]
---

# cust_oper_change_record.change_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_oper_change_record.change_type`，表页 [[tables/cust_oper_change_record]]。

## 取值

```ground:dict
dict: cust_oper_change_record__change_type
fields: [cust_oper_change_record.change_type]
values:
  BATCH: {trust: confirmed, label: 批量变更, evidence: 'code_path:OperChangeRecordApplication.java:28'}
  ASSET_AUDIT_SYNC: {trust: confirmed, label: 资产审核同步, evidence: 'code_path:OperChangeRecordApplication.java:31'}
  CUST_CHANGE_CALLBACK: {trust: confirmed, label: 企业变更回调, evidence: 'code_path:OperChangeRecordApplication.java:32'}
  MANUAL: {trust: confirmed, label: 手动变更, evidence: 'code_path:OperChangeRecordApplication.java:27'}
  AUTO_ASSIGN: {trust: confirmed, label: 自动分配, evidence: 'code_path:OperChangeRecordApplication.java:29'}
  AUTO_UPDATE: {trust: confirmed, label: 自动更新, evidence: 'code_path:OperChangeRecordApplication.java:30'}
triage: keep
```
