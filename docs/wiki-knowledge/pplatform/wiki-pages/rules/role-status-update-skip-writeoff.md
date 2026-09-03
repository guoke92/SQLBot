---
type: rule
title: 角色状态操作跳过已注销
page_key: role-status-update-skip-writeoff
domain: 客户角色与数据权限组织
status: published
aliases:
  - updateStatusByCustCompany
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_role_info.status]
scope:
  databases: [lowcode_pplatform]
---

该规则保护注销终态，避免角色状态批量更新时误改已注销角色。

## 需求背景

来自 CustRoleApplication.updateStatusByCustCompany() 的状态更新逻辑。

## 版本演进

初始语义抽取版本，后续需补充注销终态与其他状态操作的前置校验。

```ground:rule
name: 角色状态操作跳过已注销
content: updateStatusByCustCompany 查询指定企业所有角色，若角色状态已为 WRITEOFF 则跳过更新，其余角色更新为传入状态
impact: 已注销角色不会被误改状态，保护注销终态
field_targets:
  - cust_role_info.status
evidence: code_path:CustRoleApplication.java:updateStatusByCustCompany()
```

相关页面：[[cust_role_info]] [[customer-role-status-machine]]