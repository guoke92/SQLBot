---
type: caliber
title: 未注销角色口径
page_key: non-writeoff-role
domain: 客户角色与端口
status: draft
aliases:
  - 非 WRITEOFF 角色
  - 排除注销角色
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#updateStatusByCustCompany
  - db_dist: cust_role_info.status
contract_version: "0.1"
belong: calibers
---

# 未注销角色口径

在企业状态变更联动场景中，可被批量改写状态的角色集合限定为 `status <> 'WRITEOFF'`。updateStatusByCustCompany 把企业下所有非 WRITEOFF 的角色批量置为与企业 cust_status 同值，注销角色被显式跳过。

这一口径使 WRITEOFF 成为**不可逆终态**：企业解冻不会让已注销角色回到 EFFECT。它与 [[calibers/effective-company-role]] 的 enable 过滤属于不同维度，排查「角色为何没被联动」时应先看该角色是否已是 WRITEOFF。

## 需求背景

需求文档强调「不支持物理删除，只支持逻辑删除（冻结/注销）」，该口径即逻辑删除语义的落地：注销即终态，不再参与后续状态回写。

## 版本演进

- 联动逻辑增加 WRITEOFF 跳过判断后，注销与冻结在语义上彻底分离（此前二者都只是状态位）。

```ground:caliber
name: 未注销角色口径
predicate: cust_role_info.status <> 'WRITEOFF'
scope: CustRoleApplication#updateStatusByCustCompany 批量更新企业下角色状态时对 WRITEOFF 角色跳过
evidence: code_path:CustRoleApplication.java#updateStatusByCustCompany
```

## 关联

- [[tables/cust_role_info]]
- [[processes/cust-role-status]]
- [[rules/cust-status-role-cascade]]
- [[calibers/effective-company-role]]