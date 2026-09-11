---
type: process
title: 客户角色状态流转
page_key: process.cust-role-status
domain: 客户角色与端口
status: draft
aliases:
  - 客户角色状态机
  - 角色冻结解冻注销
  - cust_role_info.status 状态机
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleInfoController.java#freeze
  - code_path:CustRoleInfoController.java#unFreeze
  - code_path:CustRoleInfoController.java#logout
  - code_path:CustRoleApplication.java#operatorCustRoleStatus
  - code_path:CustCompanyInfoApplication.java#custStatusOperator
  - code_path:CustRoleApplication.java#updateStatusByCustCompany
contract_version: "0.1"
---

# 客户角色状态流转

[[tables/cust_role_info]] 的 status 是一个四态逻辑状态机：ADD（新增/待生效，DB 默认值）→ EFFECT（生效）→ FREEZE（冻结）→ WRITEOFF（注销）。冻结/解冻/注销三个动作都由 CustRoleInfoController 暴露入口，统一收敛到 CustRoleApplication#operatorCustRoleStatus 做单字段更新，不物理删除（见 [[rules/role-status-only-update]]）。

除人工动作外，本状态机还有一条**被动联动路径**：企业状态变更时角色状态跟随企业 cust_status 同值变化，且已是 WRITEOFF 的角色被跳过（见 [[rules/cust-status-role-cascade]]）。因此排查角色状态时，必须同时确认企业侧状态。

## 需求背景

需求文档主张企业状态流转为「已通过→已冻结(违规冻结)→正常(解冻)；不支持物理删除，只支持逻辑删除（冻结/注销）」。该主张与代码实现一致：企业状态变更经 custStatusOperator 联动到角色状态（FREEZE/EFFECT/WRITEOFF），角色无删除动作。

## 版本演进

- 注销（WRITEOFF）作为终态：updateStatusByCustCompany 显式跳过已是 WRITEOFF 的角色，说明注销后不再被企业状态回写「复活」。
- 状态更新由早期可能的整行更新收敛为 `CustRoleInfoDO.builder().id(x).status(y)` 的单字段 updateById，降低并发覆盖风险。

```ground:state_machine
name: 客户角色状态机
field: cust_role_info.status
states:
  - value: ADD
    label: 新增/待生效
    source: db_dist
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
transitions:
  - from: "*"
    event: freeze()
    to: FREEZE
    evidence: code_path:CustRoleInfoController.java#freeze → CustRoleApplication.java#freeze/#operatorCustRoleStatus
  - from: FREEZE
    event: unFreeze()
    to: EFFECT
    evidence: code_path:CustRoleInfoController.java#unFreeze → CustRoleApplication.java#unFreeze/#operatorCustRoleStatus
  - from: ADD|EFFECT|FREEZE
    event: logout()
    to: WRITEOFF
    evidence: code_path:CustRoleInfoController.java#logout → CustRoleApplication.java#logout/#operatorCustRoleStatus
  - from: 非WRITEOFF
    event: 企业状态变更联动(冻结/解冻/注销)
    to: FREEZE|EFFECT|WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator → CustRoleApplication.java#updateStatusByCustCompany（跳过已是 WRITEOFF 的角色）
```

## 关联

- [[tables/cust_role_info]]
- [[rules/role-status-only-update]]
- [[rules/cust-status-role-cascade]]
- [[calibers/non-writeoff-role]]
- [[calibers/effective-company-role]]