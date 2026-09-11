---
type: rule
title: 角色操作仅更新状态字段
page_key: rule.role-status-only-update
domain: 客户角色与端口
status: draft
aliases:
  - 角色冻结解冻注销只改状态
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#operatorCustRoleStatus
  - code_path:CustRoleInfoController.java#freeze
  - code_path:CustRoleInfoController.java#unFreeze
  - code_path:CustRoleInfoController.java#logout
contract_version: "0.1"
---

# 角色操作仅更新状态字段

冻结、解冻、注销三个动作的实现路径一致：先按 id 回查角色，再用 `CustRoleInfoDO.builder().id(x).status(y)` 走 updateById 做**单字段更新**，不做物理删除，也不顺手改写其他字段。这保证了角色记录始终可追溯。

对使用者的影响：任何「删除角色」的需求都应翻译为「置 [[processes/cust-role-status]] 中的某个状态位」，而不是 DELETE；同时因为只更新 status，其它列的陈旧值不会被自动纠正。

## 需求背景

需求文档要求企业角色「不支持物理删除，只支持逻辑删除」，本规则是其实现侧约束。

## 版本演进

- 从可能的整行更新收敛为单字段 updateById，减少并发下的字段覆盖。

```ground:rule
name: 角色操作仅更新状态字段
content: 冻结/解冻/注销均先按 id 回查角色，再用 CustRoleInfoDO.builder().id(x).status(y) 走 updateById 单字段更新，不做物理删除。
impact: 角色只有逻辑状态变化，无覆盖/删除动作
field_targets:
  - cust_role_info.status
evidence: code_path:CustRoleApplication.java#operatorCustRoleStatus
```

## 关联

- [[processes/cust-role-status]]
- [[tables/cust_role_info]]
- [[rules/cust-status-role-cascade]]