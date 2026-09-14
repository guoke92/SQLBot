---
type: caliber
title: 待执行异步任务口径（status='PENDING'）
page_key: async_io_task_pending
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [待执行异步任务, PENDING, 分片拉取]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.listPendingByShard"
contract_version: "0.1"
belong: calibers
---

「待执行异步任务」是 XXL-Job 分片拉取的扫描口径：按 `status='PENDING'` 取任务，结合 `MOD(task_no, shardTotal)` 分片后由 CAS 抢占执行。

状态流转见 [[async_io_task_status]]。

## 需求背景
多节点并发执行时需按任务号分片均衡负载，并保证同一任务只被一个节点执行。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 待执行异步任务
predicate: "async_io_task.status = 'PENDING'"
scope: "XXL-Job 分片拉取"
evidence: "code:AsyncIoTaskManager.listPendingByShard"
```