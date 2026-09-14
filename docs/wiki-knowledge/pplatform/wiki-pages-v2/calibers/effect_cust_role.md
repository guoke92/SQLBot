---
type: caliber
title: 已激活客户角色
page_key: effect_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - EFFECT 客户角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:unFreeze
  - db_dist:cust_role_info.status
contract_version: "0.1"
belong: calibers
---

口径「已激活客户角色」筛选状态为 EFFECT 的 [[cust_role_info]] 记录，代表当前生效的客户企业角色。

## 需求背景

解冻操作把角色状态恢复为 EFFECT，说明 EFFECT 即业务认可的“生效”态，状态机见 [[cust_role_status_machine]]。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认，当前库内 19791 条。

```ground:caliber
name: 已激活客户角色
predicate: "cust_role_info.status = 'EFFECT'"
scope: 客户角色状态为已激活
evidence: "code_path:CustRoleApplication.java:unFreeze；db_dist: EFFECT 19791"
```