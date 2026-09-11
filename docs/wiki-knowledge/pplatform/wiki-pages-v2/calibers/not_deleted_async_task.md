---
type: caliber
title: 未删除异步任务
page_key: caliber.not_deleted_async_task
domain: 租户配置
status: draft
aliases:
  - 未删除任务
  - is_deleted='0'
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - db:async_io_task.is_deleted
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
contract_version: "0.1"
---

任务分页、查询与软删除都以 `is_deleted='0'` 为未删除判定。该字段是字符串 `0/1`，既不是布尔值也不是 `Y/N`，因此调用方必须显式写字符串，见 [[concepts/is_deleted]] 与 [[processes/async_io_task_status]]。

## 需求背景

任务记录需要保留用于审计与结果文件回溯，因此采用软删除而非物理删除，查询侧统一追加未删除条件。

## 版本演进

v0.1：依据 `AsyncIoTaskManager` 中查询条件建立口径。

```yaml
caliber: 未删除异步任务
predicate: "async_io_task.is_deleted = '0'"
scope: 任务分页/查询/软删
evidence: "code:AsyncIoTaskManager.java"
```

相关页面：[[tables/async_io_task]]、[[concepts/is_deleted]]、[[calibers/pending_task_shard]]。