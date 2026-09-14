---
type: caliber
title: 角色组合校验条件
page_key: cust-role-combine-check
domain: 平台产品配置
status: draft
aliases: [角色组合校验口径, checkCustRoleCombine 条件]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:TenantProductApplication.checkCustRoleCombine
contract_version: "0.1"
belong: calibers
---

「角色组合校验条件」定义角色组合是否放行的判定方式：将平台产品配置的 `custRoleCombine` 解析为角色集合集合后，判断其是否包含当前角色集合（`custRoleCombine 解析后包含当前角色集合`）。该口径是 [[rules/cust-role-combine-check]] 的判定基准。

配置字段语义见 [[concepts/custRoleCombine]]，角色取值语义见 [[concepts/companyType]]。

## 需求背景

语义分析未提供该口径的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，口径内容来自 `TenantProductApplication.checkCustRoleCombine` 的代码证据。

```ground:caliber
name: 角色组合校验条件
predicate: "custRoleCombine 解析后包含当前角色集合"
scope: "校验企业角色组合"
evidence: TenantProductApplication.checkCustRoleCombine
```

## 关联

- 术语：[[concepts/custRoleCombine]]、[[concepts/companyType]]
- 规则：[[rules/cust-role-combine-check]]
- 表：[[tables/platform_product]]、[[tables/cust_project_rel]]