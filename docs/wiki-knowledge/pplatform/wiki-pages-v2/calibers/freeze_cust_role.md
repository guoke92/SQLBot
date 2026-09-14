---
type: caliber
title: 已冻结客户角色
page_key: freeze_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - FREEZE 客户角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:freeze
  - db_dist:cust_role_info.status
contract_version: "0.1"
belong: calibers
---

口径「已冻结客户角色」筛选状态为 FREEZE 的 [[cust_role_info]] 记录，表示因业务原因被暂停使用但仍保留的角色。

## 需求背景

冻结由 freeze 操作触发，可通过 [[cust_role_status_machine]] 中的 unFreeze 迁回 EFFECT。库内为极少数态（11 条）。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认。

```ground:caliber
name: 已冻结客户角色
predicate: "cust_role_info.status = 'FREEZE'"
scope: 客户角色状态为冻结
evidence: "code_path:CustRoleApplication.java:freeze；db_dist: FREEZE 11"
```