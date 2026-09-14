---
type: rule
title: 企业角色状态随企业状态联动更新
page_key: role_status_follow_company
domain: 平台内部服务对接
status: draft
aliases:
  - 角色状态联动
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_role_info.status]
  - semantic:state_machines[客户生命周期状态]
contract_version: "0.1"
belong: rules
---

cust_role_info.status 不独立演进，通过 updateStatusByCustCompany 随企业状态同步更新。

## 需求背景

企业在冻结、解冻、注销时（[[processes/cust_status_machine]]），其在 [[tables/cust_role_info]] 中的角色记录必须同步，否则授权与 token 换取会与企业实际状态不一致。

## 版本演进

v0：首次成页。

```ground:rule
name: 企业角色状态随企业状态联动更新
field: cust_role_info.status
condition: "企业状态变更"
effect: "updateStatusByCustCompany 同步角色状态"
evidence: code
```