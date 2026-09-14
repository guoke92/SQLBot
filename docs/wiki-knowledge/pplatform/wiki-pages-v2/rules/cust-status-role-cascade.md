---
type: rule
title: 企业状态变更联动角色状态
page_key: cust-status-role-cascade
domain: 客户角色与端口
status: draft
aliases:
  - 企业冻结解冻注销联动角色
  - updateStatusByCustCompany
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustCompanyInfoApplication.java#custStatusOperator
  - code_path:CustRoleApplication.java#updateStatusByCustCompany
  - reqdoc:cust-role-port
contract_version: "0.1"
belong: rules
---

# 企业状态变更联动角色状态

企业冻结/解冻/注销时，custStatusOperator 调用 updateStatusByCustCompany，把该企业下所有非 WRITEOFF 角色 status **批量置为与企业 cust_status 同值**（FREEZE/EFFECT/WRITEOFF）。因此角色状态不是独立演化的，它被企业状态驱动。

排查要点：角色状态与预期不符时，先看企业侧状态是否为最近一次改写的来源；注销企业会连带把角色置为 WRITEOFF，且因 [[calibers/non-writeoff-role]] 的跳过逻辑不可回退。角色自身的冻结不以企业状态变更来源为准，二者会互相覆盖，以最后一次写入为准。

## 需求背景

需求文档主张企业状态流转为「已通过→已冻结(违规冻结)→正常(解冻)；不支持物理删除，只支持逻辑删除（冻结/注销）」。该主张已由代码证实——企业状态变更正是通过本规则联动到角色状态（FREEZE/EFFECT/WRITEOFF）。

## 版本演进

- 联动范围从「生效/冻结」扩展到注销（WRITEOFF），并增加对已是 WRITEOFF 角色的跳过判断。

```ground:rule
name: 企业状态变更联动角色状态
content: 企业冻结/解冻/注销时，custStatusOperator 调用 updateStatusByCustCompany，把该企业下所有非 WRITEOFF 角色 status 批量置为与企业 cust_status 同值（FREEZE/EFFECT/WRITEOFF）。
impact: 角色状态与企业状态保持一致，注销企业会连带把角色置为 WRITEOFF
field_targets:
  - cust_role_info.status
  - cust_company_info.cust_status
evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator + CustRoleApplication.java#updateStatusByCustCompany + reqdoc:cust-role-port
```

## 关联

- [[processes/cust-role-status]]
- [[calibers/non-writeoff-role]]
- [[rules/role-status-only-update]]
- [[tables/cust_role_info]]