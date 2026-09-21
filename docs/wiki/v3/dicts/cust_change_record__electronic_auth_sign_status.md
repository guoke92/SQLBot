---
type: dict
title: cust_change_record.electronic_auth_sign_status
page_key: cust_change_record__electronic_auth_sign_status
belong: dicts
status: draft
anchors: [cust_change_record.electronic_auth_sign_status]
sources: ['database_profile:cust_change_record.electronic_auth_sign_status', 'database_schema:cust_change_record.electronic_auth_sign_status',
  'code_path:ElectronicAuthSignStatus.java:24', 'code_path:ElectronicAuthSignStatus.java:15',
  'code_path:ElectronicAuthSignStatus.java:12', 'code_path:ElectronicAuthSignStatus.java:18',
  'code_path:ElectronicAuthSignStatus.java:21']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.electronic_auth_sign_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_change_record.electronic_auth_sign_status`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__electronic_auth_sign_status
fields: [cust_change_record.electronic_auth_sign_status]
values:
  VOIDED: {trust: confirmed, label: 作废, evidence: 'code_path:ElectronicAuthSignStatus.java:24'}
  SIGNED: {trust: confirmed, label: 已签署, evidence: 'code_path:ElectronicAuthSignStatus.java:15'}
  PENDING: {trust: confirmed, label: 待签署, evidence: 'code_path:ElectronicAuthSignStatus.java:12'}
  UPLOAD_FAILED: {trust: confirmed, label: 影像上传失败, evidence: 'code_path:ElectronicAuthSignStatus.java:18'}
  FAILED: {trust: confirmed, label: 签署失败, evidence: 'code_path:ElectronicAuthSignStatus.java:21'}
triage: keep
```
