---
type: dict
title: cust_invite_info.progress
page_key: cust_invite_info__progress
belong: dicts
status: draft
anchors: [cust_invite_info.progress]
sources: ['database_profile:cust_invite_info.progress', 'database_schema:cust_invite_info.progress',
  'code_path:CustBuildStatusEnum.java:14', 'code_path:CustBuildStatusEnum.java:21',
  'code_path:CustBuildStatusEnum.java:17', 'code_path:CustBuildStatusEnum.java:24',
  'code_path:CustBuildStatusEnum.java:27', 'code_path:CustBuildStatusEnum.java:18',
  'code_path:CustBuildStatusEnum.java:30', 'code_path:CustBuildStatusEnum.java:16']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_invite_info]
---

# cust_invite_info.progress

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_invite_info.progress`，表页 [[tables/cust_invite_info]]。

## 取值

```ground:dict
dict: cust_invite_info__progress
fields: [cust_invite_info.progress]
values:
  INIT: {trust: confirmed, label: 初始化, evidence: 'code_path:CustBuildStatusEnum.java:14'}
  CUST_CONFIRM_AWAIT: {trust: confirmed, label: 待客户认证, evidence: 'code_path:CustBuildStatusEnum.java:21'}
  BUILD_SUCCESS: {trust: confirmed, label: 认证成功, evidence: 'code_path:CustBuildStatusEnum.java:17'}
  CUST_BUILDING: {trust: confirmed, label: 审核中, evidence: 'code_path:CustBuildStatusEnum.java:24'}
  CUST_CHANGE: {trust: confirmed, label: 变更, evidence: 'code_path:CustBuildStatusEnum.java:27'}
  BUILD_FAIL: {trust: confirmed, label: 认证失败, evidence: 'code_path:CustBuildStatusEnum.java:18'}
  AWAIT_CUST_CONFIRM: {trust: confirmed, label: 待客户确认, evidence: 'code_path:CustBuildStatusEnum.java:30'}
  BUILDING: {trust: confirmed, label: 建档中, evidence: 'code_path:CustBuildStatusEnum.java:16'}
triage: keep
```
