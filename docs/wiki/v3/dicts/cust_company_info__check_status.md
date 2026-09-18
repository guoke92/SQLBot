---
type: dict
title: cust_company_info.check_status
page_key: cust_company_info__check_status
belong: dicts
status: draft
anchors: [cust_company_info.check_status]
sources: ['database_profile:cust_company_info.check_status', 'database_schema:cust_company_info.check_status',
  'code_path:OperApiConstants.java:203', 'code_path:OperApiConstants.java:204']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.check_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_company_info.check_status`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__check_status
fields: [cust_company_info.check_status]
values:
  CUST_CHECK_PASS: {trust: confirmed, label: 审核通过, evidence: 'code_path:OperApiConstants.java:203'}
  CUST_CHECK_BACKTOCUSTOM: {trust: confirmed, label: 待客户确认, evidence: 'code_path:OperApiConstants.java:204'}
  CUST_CHECK_REJECT: {trust: confirmed, label: 审核不通过, evidence: 'code_path:OperApiConstants.java:203'}
  CUST_CHECK_CHECKING: {trust: confirmed, label: 审核中, evidence: 'code_path:OperApiConstants.java:203'}
  CUST_CHECK_INIT: {trust: confirmed, label: 待审核, evidence: 'code_path:OperApiConstants.java:203'}
  EFFECT: {trust: proposed}
  CUST_BACK: {trust: confirmed, label: 退回, evidence: 'code_path:OperApiConstants.java:204'}
triage: keep
```
