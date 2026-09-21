---
type: dict
title: cust_change_record.status
page_key: cust_change_record__status
belong: dicts
status: draft
anchors: [cust_change_record.status]
sources: ['database_profile:cust_change_record.status', 'database_schema:cust_change_record.status',
  'code_path:OperApiConstants.java:203', 'code_path:OperApiConstants.java:204']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_change_record.status`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__status
fields: [cust_change_record.status]
values:
  CUST_CHECK_INIT: {trust: confirmed, label: 待审核, evidence: 'code_path:OperApiConstants.java:203'}
  CUST_CHECK_CHECKING: {trust: confirmed, label: 审核中, evidence: 'code_path:OperApiConstants.java:203'}
  CUST_CHECK_PASS: {trust: confirmed, label: 审核通过, evidence: 'code_path:OperApiConstants.java:203'}
  CUST_CHECK_REJECT: {trust: confirmed, label: 审核不通过, evidence: 'code_path:OperApiConstants.java:203'}
  CUST_CHECK_BACKTOCUSTOM: {trust: confirmed, label: 待客户确认, evidence: 'code_path:OperApiConstants.java:204'}
  CUST_BACK: {trust: confirmed, label: 退回, evidence: 'code_path:OperApiConstants.java:204'}
```
