---
type: rule
title: 进入产品前项目状态检查
page_key: goto-product-project-status-check
domain: 平台产品配置
status: draft
aliases: [项目状态检查, gotoProductSupplierFirstRelatedProject]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatformProductApplication.gotoProductSupplierFirstRelatedProject
contract_version: "0.1"
belong: rules
---

多项目产品且产品为通用产品时，进入产品前检查企业关联项目是否生效，未生效则禁止进入。该规则以「多项目 + 通用产品」为前提条件，通用产品的判定见 [[calibers/general-product-scope]]；字段落点为 `tenant_project.project_status` 与 [[tables/cust_project_rel]]。

## 需求背景

语义分析未提供该规则的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，规则内容来自 `PlatformProductApplication.gotoProductSupplierFirstRelatedProject` 的代码证据。规则 field_targets 中出现的 `tenant_project` 表本次语义分析未提供字段级证据，暂不在表目录建档。

```ground:rule
name: 进入产品前项目状态检查
content: "多项目产品且产品为通用产品时，检查企业关联项目是否生效，未生效则禁止进入。"
impact: "阻止进入产品。"
field_targets:
  - tenant_project.project_status
  - cust_project_rel
evidence: PlatformProductApplication.gotoProductSupplierFirstRelatedProject
```

## 关联

- 表：[[tables/cust_project_rel]]、[[tables/platform_product]]
- 口径：[[calibers/general-product-scope]]
- 同类校验：[[rules/goto-product-company-type-check]]