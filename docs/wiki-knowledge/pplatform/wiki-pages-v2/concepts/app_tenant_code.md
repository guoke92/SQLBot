---
type: concept
title: 逻辑租户
page_key: app_tenant_code
domain: 平台事件监听与同步
status: draft
aliases:
  - appTenantCode
  - AppTenantCode
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
contract_version: "0.1"
maps_to: client_api_sync_error.app_tenant_code
field_targets:
  - client_api_sync_error.app_tenant_code
adjudication: boundary
also_confused_with:
  - client_api_sync_error.db_tenant_code
belong: concepts
field_targets: [client_api_sync_error.app_tenant_code]
---

「逻辑租户」指应用层的租户标识，与数据隔离租户是两件事，二者在同一张表上并列存在。

## 需求背景

[[client_api_sync_error]].`app_tenant_code` 为逻辑/应用租户，实测恒为 `base`；`db_tenant_code` 才是数据隔离租户，见 [[db_tenant_code]]。做数据筛选、报表分组时误用前者会得到单一分组。

## 版本演进

- 平台同步场景下逻辑租户长期为 `base`，说明本主题的租户差异主要体现在数据租户维度而非应用维度。
- 代码中命名为 `appTenantCode` / `AppTenantCode`，与列名 `app_tenant_code` 需人工映射。