---
type: concept
title: 数据租户标识
page_key: db_tenant_code
domain: 租户迁移
status: published
aliases: ["dbTenantCode", "db_tenant_code"]
oid: 1
sources: ["semantic_analysis_v0.1"]
contract_version: "0.1"
maps_to: "CustCompanyInfoDO.dbTenantCode / Customer DO.dbTenantCode / DB列 db_tenant_code"
also_confused_with: ["appTenantCode", "app_tenant_code"]
adjudication: boundary
scope:
  databases: [lowcode_pplatform]
---

# 数据租户标识

业务定位：数据租户标识（`db_tenant_code`）是物理数据隔离维度，用于区分底层数据归属，与逻辑租户标识（`app_tenant_code`）不同。

## 需求背景

在迁移场景中，数据租户标识用于确定数据实际存储的物理租户。它与逻辑租户标识分离，迁移过程中可能跨越不同的 `dbTenantCode` 而保留逻辑租户。二者不可混淆。

## 版本演进

暂无。

[[app_tenant_code]]