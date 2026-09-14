---
type: concept
title: 数据租户
page_key: db_tenant_code
domain: 平台事件监听与同步
status: draft
aliases:
  - dbTenantCode
  - db_tenant_code
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
maps_to: client_api_sync_error.db_tenant_code
field_targets:
  - client_api_sync_error.db_tenant_code
  - cust_build_record.dbTenantCode
adjudication: boundary
also_confused_with:
  - client_api_sync_error.app_tenant_code
belong: concepts
field_targets: [client_api_sync_error.db_tenant_code]
sources: ["enrich:wiki-admin"]
---

「数据租户」是真正的数据隔离维度，代码通过 `MetaDataThreadLocalConfig.setDbTenantCode` 切换上下文。

## 需求背景

同步任务执行前会先 `setDbTenantCode(dbTenantCode)`，见 [[cust_sync_by_role]]；补偿任务则从 [[cust_build_record]].`dbTenantCode` 还原建档企业所属租户后再重放。全量查询使用 `'all'`。与逻辑租户的区别见 [[app_tenant_code]]。

## 版本演进

- 线程上下文方式意味着同步链路对租户上下文有隐式依赖，跨租户批次混跑时需要显式重置。

相关：[[client_api_sync_error]]
