---
type: rule
title: 跨租户查询需显式设置 dbTenantCode="all"
page_key: cross_tenant_query_all
domain: 平台内部服务对接
status: draft
aliases:
  - 跨租户查询
  - dbTenantCode all
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.db_tenant_code]
contract_version: "0.1"
belong: rules
---

Provider 层默认按当前租户隔离数据，需要跨租户读取时必须通过 MetaDataThreadLocalConfig.setDbTenantCode("all") 显式放宽。

## 需求背景

该开关作用于 [[tables/cust_company_info]] 等带 db_tenant_code 的表（见 [[concepts/db_tenant_code_bridge]]）。跨租户查询属于越权边界，仅在平台侧内部对接场景使用。

## 版本演进

v0：首次成页。

```ground:rule
name: 跨租户查询需显式设置 dbTenantCode="all"
field: cust_company_info.db_tenant_code
condition: "MetaDataThreadLocalConfig.setDbTenantCode(\"all\")"
effect: "Provider 层跨租户查询"
evidence: code
```