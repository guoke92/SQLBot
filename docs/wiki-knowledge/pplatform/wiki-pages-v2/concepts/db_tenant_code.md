---
type: concept
title: dbTenantCode
page_key: concept.db_tenant_code
domain: 租户配置
status: draft
aliases:
  - db_tenant_code
  - 数据租户标识
  - 数据库租户编码
  - 租户编码
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.db_tenant_code
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
maps_to: tenant_setting_config.db_tenant_code
field_targets:
  - tenant_setting_config.db_tenant_code
adjudication: boundary
also_confused_with:
  - tenantFlgEn
sources: ["enrich:wiki-admin"]
---

`dbTenantCode` 是数据租户标识/数据库租户编码，承担多租户数据隔离主键职责，对应 [[tables/tenant_setting_config]] 的唯一键 `db_tenant_code`。与之最易混淆的是 [[concepts/tenant_flg_en]]：初始化时 `tenant_flg_en` 会被写成与 `dbTenantCode` 相等，但后续语义分叉——在共享假租户场景下，同一个 `db_tenant_code` 可以对应多个 `tenant_flg_en`（见 [[calibers/shared_fake_tenant]]）。因此二者不可互换使用：`dbTenantCode` 回答「数据属于哪个租户库域」，`tenantFlgEn` 回答「以哪个项目/品牌标识对外」。

## 需求背景

多租户隔离需要一个稳定、唯一的库级主键，租户侧几乎所有查询（含 [[calibers/enabled_tenant]]）都以此为入口，因此该术语的边界必须在需求与实现两侧保持一致。

## 版本演进

v0.1：确立与 `tenantFlgEn` 的边界裁决（boundary），记录初始化相等、后续分叉的事实。

相关：[[tenant_setting_config]]
