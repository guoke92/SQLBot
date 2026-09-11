---
type: concept
title: tenantFlgEn
page_key: concept.tenant_flg_en
domain: 租户配置
status: draft
aliases:
  - tenant_flg_en
  - 项目标识（英文）
  - 租户英文标识
  - projectMark
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.tenant_flg_en
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
maps_to: tenant_setting_config.tenant_flg_en
field_targets:
  - tenant_setting_config.tenant_flg_en
adjudication: boundary
also_confused_with:
  - dbTenantCode
sources: ["enrich:wiki-admin"]
---

`tenantFlgEn` 是租户在产融侧的项目级英文标识，Excel 导入列名「项目标识(产融 tenant_flg_en)」即指该字段。它既被用于租户查询，又被当作项目标识使用，因此与 [[concepts/db_tenant_code]] 的边界必须显式声明（见 [[calibers/shared_fake_tenant]]、[[calibers/lls_self_tenant]]）。初始化时二者被写成相等，但共享租户下同 `dbTenantCode` 可有多 `tenantFlgEn`。

## 需求背景

同一数据租户要承载多个项目/品牌标识对外展示与服务，项目标识因此从租户标识中独立出来，成为可一对多的维度。

## 版本演进

v0.1：确立与 `dbTenantCode` 的边界裁决（boundary）。

相关：[[tenant_setting_config]]
