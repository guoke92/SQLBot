---
type: rule
title: 企业角色组合校验
page_key: rules/cust-role-combine-check
domain: 平台产品配置
status: draft
aliases: [角色组合校验, checkCustRoleCombine]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.checkCustRoleCombine
contract_version: "0.1"
---

同一企业在同一产品下拥有多个角色时，系统校验该角色组合是否在平台产品配置的 `custRoleCombine` 允许范围内，不在范围内则抛出异常，阻止不合法的角色组合。

字段落点为 [[tables/platform_product]] 的 `cust_role_combine` 与 [[tables/cust_project_rel]] 的 `company_type`；判定口径见 [[calibers/cust-role-combine-check]]，术语见 [[concepts/custRoleCombine]] 与 [[concepts/companyType]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `TenantProductApplication.checkCustRoleCombine` 的代码证据。

```ground:rule
name: 企业角色组合校验
content: "同一企业在同一产品下拥有多个角色时，校验角色组合是否在平台产品配置的 custRoleCombine 中，不在则抛出异常。"
impact: "阻止不合法的角色组合。"
field_targets:
  - platform_product.cust_role_combine
  - cust_project_rel.company_type
evidence: TenantProductApplication.checkCustRoleCombine
```

## 关联

- 表：[[tables/platform_product]]、[[tables/cust_project_rel]]、[[tables/cust_company_info]]
- 口径：[[calibers/cust-role-combine-check]]
- 术语：[[concepts/custRoleCombine]]、[[concepts/companyType]]