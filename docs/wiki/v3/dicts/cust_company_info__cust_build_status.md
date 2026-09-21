---
type: dict
title: cust_company_info.cust_build_status
page_key: cust_company_info__cust_build_status
belong: dicts
status: draft
anchors: [cust_company_info.cust_build_status]
sources: ['database_profile:cust_company_info.cust_build_status', 'database_schema:cust_company_info.cust_build_status',
  'code_path:CustBuildStatusEnum.java:17', 'code_path:CustBuildStatusEnum.java:14',
  'code_path:CustBuildStatusEnum.java:21', 'code_path:CustBuildStatusEnum.java:18',
  'code_path:CustBuildStatusEnum.java:24', 'code_path:CustBuildStatusEnum.java:27',
  'code_path:CustBuildStatusEnum.java:30', 'code_path:CustBuildStatusEnum.java:20',
  'code_path:CustBuildStatusEnum.java:19', 'code_path:CustBuildStatusEnum.java:16',
  'code_path:CustBuildStatusEnum.java:23', 'code_path:CustBuildStatusEnum.java:25',
  'code_path:CustBuildStatusEnum.java:15', 'code_path:CustBuildStatusEnum.java:26']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cust_build_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_company_info.cust_build_status`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cust_build_status
fields: [cust_company_info.cust_build_status]
values:
  BUILD_SUCCESS: {trust: confirmed, label: 认证成功, evidence: 'code_path:CustBuildStatusEnum.java:17'}
  INIT: {trust: confirmed, label: 初始化, evidence: 'code_path:CustBuildStatusEnum.java:14'}
  CUST_CONFIRM_AWAIT: {trust: confirmed, label: 待客户认证, evidence: 'code_path:CustBuildStatusEnum.java:21'}
  BUILD_FAIL: {trust: confirmed, label: 认证失败, evidence: 'code_path:CustBuildStatusEnum.java:18'}
  CUST_BUILDING: {trust: confirmed, label: 审核中, evidence: 'code_path:CustBuildStatusEnum.java:24'}
  CUST_CHANGE: {trust: confirmed, label: 变更, evidence: 'code_path:CustBuildStatusEnum.java:27'}
  AWAIT_CUST_CONFIRM: {trust: confirmed, label: 待客户确认, evidence: 'code_path:CustBuildStatusEnum.java:30'}
  BUILD_ACTIVATE: {trust: confirmed, label: 待激活, evidence: 'code_path:CustBuildStatusEnum.java:20'}
  BUILD_BACK: {trust: confirmed, label: 退回, evidence: 'code_path:CustBuildStatusEnum.java:19'}
  BUILDING: {trust: confirmed, label: 建档中, evidence: 'code_path:CustBuildStatusEnum.java:16'}
  CUST_AUDIT_AWAIT: {trust: confirmed, label: 待审核, evidence: 'code_path:CustBuildStatusEnum.java:23'}
  CUST_BUILD_SUCCESS: {trust: confirmed, label: 审核通过, evidence: 'code_path:CustBuildStatusEnum.java:25'}
  TO_BE_BUILD: {trust: confirmed, label: 未建档, evidence: 'code_path:CustBuildStatusEnum.java:15'}
  CUST_BUILD_FAIL: {trust: confirmed, label: 审核拒绝, evidence: 'code_path:CustBuildStatusEnum.java:26'}
triage: keep
```
