---
type: rule
title: 角色状态冻结/解冻/注销规则
page_key: role_status_freeze_logout
domain: 客户角色与端口
status: draft
aliases:
  - 角色状态变更规则
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:freeze
  - code_path:CustRoleApplication.java:unFreeze
  - code_path:CustRoleApplication.java:logout
  - code_path:CustRoleApplication.java:updateStatusByCustCompany
contract_version: "0.1"
belong: rules
---

该规则约束 [[cust_role_info]].status 的变更取值与边界条件，状态机全貌见 [[cust_role_status_machine]]。

## 需求背景

冻结、解冻、注销分别把状态置为 FREEZE、EFFECT、WRITEOFF；批量按企业更新状态时跳过已 WRITEOFF 的记录，保证注销终态不被批量动作覆盖。按状态切分的口径见 [[freeze_cust_role]]、[[effect_cust_role]]、[[writeoff_cust_role]]。

## 版本演进

- v0（draft）：依据 4 个代码路径成页。

```ground:rule
name: 角色状态冻结/解冻/注销规则
content: "冻结置 status=FREEZE，解冻置 status=EFFECT，注销置 status=WRITEOFF；批量更新企业角色状态时跳过已注销（WRITEOFF）的记录。"
impact: 影响 cust_role_info.status
field_targets:
  - cust_role_info.status
evidence: "code_path:CustRoleApplication.java:freeze, unFreeze, logout, updateStatusByCustCompany"
```