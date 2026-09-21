---
type: dict
title: cust_change_record.electronic_auth_sign_status
page_key: cust_change_record__electronic_auth_sign_status
belong: dicts
status: draft
anchors: [cust_change_record.electronic_auth_sign_status]
sources: ['database_profile:cust_change_record.electronic_auth_sign_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.electronic_auth_sign_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_change_record.electronic_auth_sign_status`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__electronic_auth_sign_status
fields: [cust_change_record.electronic_auth_sign_status]
values:
  VOIDED: {trust: proposed}
  SIGNED: {trust: proposed}
  PENDING: {trust: proposed}
triage: keep
```
