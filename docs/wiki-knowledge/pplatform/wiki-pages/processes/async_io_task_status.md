---
type: process
title: async_io_task.status 状态机
page_key: async_io_task_status
belong: processes
domain: 异步任务与数据同步
status: published
aliases: []
oid: 1
sources: ["code", "db_dist"]
contract_version: "0.1"
field_targets: [async_io_task.status]
scope:
  databases: [lowcode_pplatform]
---

async_io_task.status 定义了异步任务执行状态从 PENDING 到 RUNNING 再到 SUCCESS 或 FAILED 的流转。相关表：[[async_io_task]]。

## 需求背景

任务调度需要可靠的状态流转，包括超时处理与成功失败标记。

## 版本演进

v0.1 提取状态机及转换证据。

```ground:process
name: async_io_task.status
field: status
states:
  - value: PENDING
    label: 待处理
    source: code_enum
  - value: RUNNING
    label: 运行中
    source: db_dist
  - value: SUCCESS
    label: 成功
    source: db_dist
  - value: FAILED
    label: 失败
    source: db_dist
transitions:
  - from: PENDING
    event: markRunning/调度执行
    to: RUNNING
    evidence: code_path:AsyncIoTaskManager.markRunning
  - from: RUNNING
    event: markSuccessWithFile/markSuccessWithResult
    to: SUCCESS
    evidence: code_path:AsyncIoTaskManager.markSuccessWithFile
  - from: RUNNING
    event: markFailed/markImportFailed
    to: FAILED
    evidence: code_path:AsyncIoTaskManager.markFailed
  - from: RUNNING
    event: markRunningTimeout
    to: FAILED
    evidence: code_path:AsyncIoTaskManager.markRunningTimeout
```