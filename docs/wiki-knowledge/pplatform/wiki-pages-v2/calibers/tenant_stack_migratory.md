---
type: caliber
title: 堆栈/迁移标识口径（is_stack → migratory/stock）
page_key: caliber.tenant_stack_migratory
domain: 平台内部服务对接
status: draft
aliases:
  - is_stack
  - 迁移标识
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_setting_config.is_stack]
  - semantic:field_semantics[tenant_product.is_migratory]
contract_version: "0.1"
---

租户级 is_stack 决定小程序租户信息 DTO 中 migratory/stock 的取值，产品级另有 is_migratory 表示产品迁移状态。

## 需求背景

两者分属租户层与产品层：租户级标识影响小程序信息输出（PlatMiniProgramTenantInfoDto），产品级标识表达 [[tables/tenant_product]] 的开通产品是否已迁移，不可互相替代。

## 版本演进

v0：首次成页。

```ground:caliber
name: 堆栈/迁移标识口径
field: tenant_setting_config.is_stack
values:
  - "'Y'"
  - "'N'"
criterion: "决定 PlatMiniProgramTenantInfoDto 的 migratory/stock"
related_fields:
  - tenant_product.is_migratory
evidence: code
```