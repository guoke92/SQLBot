---
type: concept
title: tenantCode 租户标识
page_key: tenantCode
domain: 平台产品配置
status: draft
aliases: [tenantCode, dbTenantCode, 数据租户标识]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:platform_product.db_tenant_code
  - db:platform_product.app_tenant_code
  - code:cust_company_info.db_tenant_code
maps_to: platform_product.db_tenant_code
adjudication: boundary
also_confused_with: [appTenantCode]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
field_targets: [platform_product.db_tenant_code]
---

tenantCode 与 dbTenantCode 指数据租户标识，映射到 [[tables/platform_product]] 的 `db_tenant_code`，[[tables/cust_company_info]] 也以同名 `db_tenant_code` 承载该语义。

边界：`dbTenantCode` 是数据租户标识，用于数据隔离；`appTenantCode` 是逻辑租户标识，用于应用层。两者同表并存但语义层级不同，不可互换。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/platform_product]]、[[tables/cust_company_info]]
- 术语：[[concepts/productCode]]

相关：[[platform_product]]
