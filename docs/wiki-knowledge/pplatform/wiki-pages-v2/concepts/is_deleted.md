---
type: concept
title: 软删除标记
page_key: concept.is_deleted
domain: 租户配置
status: draft
aliases:
  - is_deleted
  - 删除标识
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
    - lowcode-pplatform-tenant-management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
contract_version: "0.1"
maps_to: async_io_task.is_deleted / operation_user.deleted
field_targets:
  - async_io_task.is_deleted
  - operation_user.deleted
adjudication: boundary
also_confused_with: []
sources: ["enrich:wiki-admin"]
---

软删除标记在各表使用字符串 `0/1`，既不是布尔值也不是 `Y/N`。查询未删除数据必须显式写 `'0'`（见 [[calibers/not_deleted_async_task]]）；若按 `Y/N` 或布尔语义书写条件，会静默返回错误结果集。注意部分表列名为 `deleted`，取值约定相同但列名不同，不可按列名统一拼接。

## 需求背景

任务与用户记录需要保留用于审计与结果回溯，因此采用软删除；字符串取值来自历史实现约定，短期内不做类型收敛。

## 版本演进

v0.1：登记 `0/1` 字符串取值约定与显式 `'0'` 查询要求。

相关：[[async_io_task]] [[operation_user]]
