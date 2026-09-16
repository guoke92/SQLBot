---
type: process
title: 异步任务状态机
page_key: async_io_task_flow
domain: 租户配置/灰度/运营邮件
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - async_io_task.status
---

登记 PENDING，抢占 RUNNING，结束 SUCCESS 或 FAILED；RUNNING 超时也会 FAILED。

```ground:process
name: 异步任务状态机
field: async_io_task.status
states:
  - value: PENDING
    label: PENDING
    source: code_enum
  - value: RUNNING
    label: RUNNING
    source: code_enum
  - value: SUCCESS
    label: SUCCESS
    source: code_enum
  - value: FAILED
    label: FAILED
    source: code_enum
transitions:
  - from: PENDING
    event: 分片领取执行
    to: RUNNING
    evidence: "code_path:AsyncIoTaskManager.java:113"
  - from: RUNNING
    event: 执行成功
    to: SUCCESS
    evidence: "code_path:AsyncIoTaskManager.java:122"
  - from: RUNNING
    event: 失败或超时
    to: FAILED
    evidence: "code_path:AsyncIoTaskManager.java:147"
```
