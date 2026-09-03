---
type: concept
title: 逻辑租户标识
page_key: app_tenant_code
domain: 租户迁移
status: published
aliases: ["appTenantCode"]
oid: 1
sources: ["semantic_analysis_v0.1"]
contract_version: "0.1"
maps_to: "app_tenant_code"
also_confused_with: ["dbTenantCode"]
adjudication: boundary
scope:
  databases: [lowcode_pplatform]
---

# 逻辑租户标识

业务定位：逻辑租户标识（`app_tenant_code`）是逻辑层面的租户标识，与数据租户标识（`db_tenant_code`）分离。迁移中可能跨数据租户保留逻辑租户。

## 需求背景

逻辑租户与数据租户分离后，同一逻辑租户的数据可能分布在不同的物理数据租户下。`app_tenant_code` 用于在业务层面标识租户，迁移时需保持其稳定性。

## 版本演进

暂无。

[[数据租户标识]]