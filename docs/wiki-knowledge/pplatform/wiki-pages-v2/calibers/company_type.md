---
type: caliber
title: 企业角色口径（company_type）
page_key: company_type
domain: 租户产品
status: draft
aliases: [企业角色, company_type]
oid: 1
scope:
  databases: []
sources:
  - db:tenant_product_menu
  - db:tenant_product_menu_res
contract_version: "0.1"
belong: calibers
---

企业角色口径描述菜单配置中「角色」维度的可选值。[[tables/tenant_product_menu]] 的实测值域为 9 类，[[tables/tenant_product_menu_res]] 只有其中 4 类，说明后者面向的角色更窄。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该口径决定同产品在不同角色下可见的菜单集合，与 [[tables/tenant_product_menu]]、[[tables/tenant_product_menu_res]] 的配置共同生效。

## 版本演进
- 两张表的角色值域不一致（CORE_MANAGER/DEALER/FINANCE/PLATFORM_OPERATOR/PROJECT_COMPANY 只出现在 menu 表），是否为业务差异需确认。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:caliber
name: 企业角色口径
fields:
  - table: tenant_product_menu
    field: company_type
    values: [CORE, CORE_MANAGER, CORPORATION_COMPANY, DEALER, FINANCE, PLATFORM_OPERATOR, PLATFORM_OPERATOR_COMPANY, PROJECT_COMPANY, SUPPLIER]
    definition: 企业角色；DB 实测 CORE/CORE_MANAGER/CORPORATION_COMPANY/DEALER/FINANCE/PLATFORM_OPERATOR/PLATFORM_OPERATOR_COMPANY/PROJECT_COMPANY/SUPPLIER
    evidence: db
  - table: tenant_product_menu_res
    field: company_type
    values: [CORE, CORPORATION_COMPANY, PLATFORM_OPERATOR_COMPANY, SUPPLIER]
    definition: 企业角色；DB 实测 CORE/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY/SUPPLIER
    evidence: db
```