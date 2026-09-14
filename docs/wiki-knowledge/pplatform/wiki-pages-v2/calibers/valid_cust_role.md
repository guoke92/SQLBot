---
type: caliber
title: 有效客户角色
page_key: valid_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - enable=Y 客户角色
  - 有效角色
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:getCompanyTypeByCompanyCode
contract_version: "0.1"
belong: calibers
---

口径「有效客户角色」用于查询当前企业已存在的企业角色，事实表见 [[cust_role_info]]，与状态维度口径 [[effect_cust_role]] 可组合使用。

## 需求背景

查询企业的角色集合时以 enable='Y' 作为逻辑启用过滤，避免返回已逻辑删除的记录；该口径被 getCompanyTypeByCompanyCode 直接使用。

## 版本演进

- v0（draft）：依据代码路径导出。

```ground:caliber
name: 有效客户角色
predicate: "cust_role_info.enable = 'Y'"
scope: 查询当前企业已存在的企业角色
evidence: "code_path:CustRoleApplication.java:getCompanyTypeByCompanyCode 使用 enable=Y"
```