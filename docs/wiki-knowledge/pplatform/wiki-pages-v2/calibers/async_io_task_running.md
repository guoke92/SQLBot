---
type: caliber
title: 运行中超时异步任务口径（status='RUNNING'）
page_key: async_io_task_running
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [运行中超时任务, RUNNING, 超时清理]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.markRunningTimeout"
  - "db:async_io_task.status RUNNING=3"
contract_version: "0.1"
belong: calibers
---

「运行超时异步任务」是超时清理任务的扫描集合：处于 `status='RUNNING'` 且停留超过 timeoutMinutes 的任务会被兜底置为 FAILED。它同时是排查悬挂任务的观测口径。

状态流转见 [[async_io_task_status]]。

## 需求背景
节点强杀或 OOM 会让任务永久停留执行中，需要超时扫描将其收敛为失败以便用户重试。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 运行超时异步任务
predicate: "async_io_task.status = 'RUNNING'"
scope: "超时清理任务扫描集合"
evidence: "code:AsyncIoTaskManager.markRunningTimeout；db:RUNNING=3"
```