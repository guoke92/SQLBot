---
type: caliber
title: 企业启用角色+指定角色类型精确匹配口径
page_key: enterprise-enabled-role-and-type
belong: calibers
domain: 客户角色与数据权限组织
status: published
aliases:
  - getCompanyTypeByCompanyCodeAndType
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_role_info.enable, cust_role_info.ref_cust_company_info, cust_role_info.role_type]
scope:
  databases: [lowcode_pplatform]
---

该口径描述按企业编码和角色类型精确查询单个启用角色。

## 需求背景

支撑需要精确匹配某企业某角色类型的场景，如企业管理员判定或角色唯一性校验。

## 版本演进

初始语义抽取版本，后续需补充查询结果为空时的处理规则。

```ground:caliber
name: 企业启用角色+指定角色类型精确匹配
predicate: cust_role_info.enable = 'Y' AND cust_role_info.ref_cust_company_info = {companyCode} AND cust_role_info.role_type = {roleType}
scope: 按企业编码和角色类型精确查询单个角色
evidence: code_path:CustRoleApplication.java:getCompanyTypeByCompanyCodeAndType()
```

相关页面：[[cust_role_info]] [[enterprise-role]]