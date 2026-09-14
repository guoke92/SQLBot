---
type: caliber
title: 待执行任务分片
page_key: pending_task_shard
domain: 租户配置
status: draft
aliases:
  - 待执行任务分片
  - listPendingByShard
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - db:async_io_task.task_no
  - db:async_io_task.status
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:listPendingByShard
contract_version: "0.1"
belong: calibers
---

XXL-Job 分片广播拉取待执行任务时，用 `MOD(task_no, shardTotal) = shardIndex` 在分片间均分任务号，并叠加 `status='PENDING'` 与未删除条件。由于 `task_no` 是 DB 自增列，取模天然形成近似均匀分布，无需额外调度表。

## 需求背景

异步任务量随导入导出使用量增长，单机轮询会造成处理延迟；使用分片广播 + 取模可以让每个执行器实例只处理自己的一份任务，同时避免多实例重复抢占（抢占仍由 CAS 状态迁移兜底，见 [[processes/async_io_task_status]]）。

## 版本演进

v0.1：依据 `listPendingByShard` 的查询构造建立口径。

```yaml
caliber: 待执行任务分片
predicate: "async_io_task.status = 'PENDING' AND MOD(task_no, shardTotal) = shardIndex AND is_deleted <> '1'"
scope: XXL-Job 分片广播拉取
evidence: "code:AsyncIoTaskManager.java:listPendingByShard"
```

相关页面：[[tables/async_io_task]]、[[processes/async_io_task_status]]、[[calibers/not_deleted_async_task]]。