---
type: caliber
title: 已注销客户角色
page_key: writeoff_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - WRITEOFF 客户角色
  - 注销角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:logout
  - code_path:CustRoleApplication.java:updateStatusByCustCompany
  - db_dist:cust_role_info.status
contract_version: "0.1"
belong: calibers
---

口径「已注销客户角色」筛选状态为 WRITEOFF 的 [[cust_role_info]] 记录。注销是不可逆的终态：批量更新状态时会显式跳过这些记录（见 [[role_status_freeze_logout]]）。

## 需求背景

logout 把角色置为 WRITEOFF；updateStatusByCustCompany 在批量更新时跳过已注销记录，因此本口径也用于识别“不应再被业务动作影响”的角色。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认，当前库内 44 条。

```ground:caliber
name: 已注销客户角色
predicate: "cust_role_info.status = 'WRITEOFF'"
scope: 客户角色状态为注销
evidence: "code_path:CustRoleApplication.java:logout；db_dist: WRITEOFF 44"
```