---
type: rule
title: CAS 更新到 RUNNING
page_key: CAS更新到RUNNING
belong: rules
domain: 异步任务与数据同步
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [async_io_task.start_time, async_io_task.status]
scope:
  databases: [lowcode_pplatform]
---

该规则通过 CAS 防止任务被重复执行。相关表：[[async_io_task]]。

## 需求背景

并发调度时需要保证任务只被一个执行器处理。

## 版本演进

v0.1 提取。

```ground:rule
name: CAS 更新到 RUNNING
content: 仅当 status='PENDING' 时才能将任务更新为 'RUNNING' 并写入 start_time
impact: 防止任务被重复执行
field_targets:
  - async_io_task.status
  - async_io_task.start_time
evidence: code_path:AsyncIoTaskManager.markRunning
```