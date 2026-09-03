---
type: caliber
title: 企业启用角色列表口径
page_key: enterprise-enabled-role-list
domain: 客户角色与数据权限组织
status: published
aliases:
  - getCompanyTypeByCompanyCode
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_role_info.enable, cust_role_info.ref_cust_company_info]
scope:
  databases: [lowcode_pplatform]
---

该口径描述按企业编码查询未禁用角色列表，不排除冻结或注销状态。

## 需求背景

支撑企业角色列表查询，用于角色类型集合展示和后续角色相关业务。

## 版本演进

初始语义抽取版本，后续需补充口径参数与返回结构。

```ground:caliber
name: 企业启用角色列表
predicate: cust_role_info.enable = 'Y' AND cust_role_info.ref_cust_company_info = {companyCode}
scope: 按企业编码查询未禁用角色，不排除冻结/注销
evidence: code_path:CustRoleApplication.java:getCompanyTypeByCompanyCode()
```

相关页面：[[cust_role_info]] [[enterprise-role]]