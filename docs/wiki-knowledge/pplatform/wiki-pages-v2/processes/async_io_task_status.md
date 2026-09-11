---
type: process
title: 异步导入导出任务状态（async_io_task.status）
page_key: process.async_io_task_status
domain: 租户配置
status: draft
aliases:
  - 异步任务状态
  - 导入导出任务状态
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java:handleNonStreamResult
contract_version: "0.1"
---

任务从 PENDING 开始，由 XXL-Job 分片抢单（见 [[calibers/pending_task_shard]]）后以 CAS 置为 RUNNING，随后分化多条终态路径：正常成功写 SUCCESS 并回填结果文件或结果 JSON；抛异常、导入部分失败、或超过 `timeoutMinutes` 被超时清理，都落 FAILED。FAILED 的 `file_url` 语义是错误文件下载地址，SUCCESS 则是结果文件地址。

## 需求背景

导入部分失败时业务代码可能正常返回，但运营侧需要明确感知失败并拿到错误行文件，因此把「含失败行」也判定为 FAILED；同时为防止任务卡死在 RUNNING，引入超时清理路径将其收敛到 FAILED。

## 版本演进

v0.1：登记当前代码枚举中的四个状态与六条迁移路径。

```yaml
state_machine: 异步导入导出任务状态
field: async_io_task.status
states:
  - value: "PENDING"
    label: 待执行
    source: code_enum
  - value: "RUNNING"
    label: 执行中
    source: code_enum
  - value: "SUCCESS"
    label: 成功
    source: code_enum
  - value: "FAILED"
    label: 失败
    source: code_enum
transitions:
  - from: "PENDING"
    event: 调度抢到任务 markRunning(CAS)
    to: "RUNNING"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunning"
  - from: "RUNNING"
    event: 执行成功（下载流/结果落库）
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithFile"
  - from: "RUNNING"
    event: 执行成功（结果 JSON）
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithResult"
  - from: "RUNNING"
    event: 执行抛异常
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markFailed"
  - from: "RUNNING"
    event: 导入部分失败（业务正常返回但含失败行）
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java:handleNonStreamResult"
  - from: "RUNNING"
    event: 超时清理（超过 timeoutMinutes）
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunningTimeout"
```

相关页面：[[tables/async_io_task]]、[[calibers/pending_task_shard]]、[[calibers/not_deleted_async_task]]、[[concepts/is_deleted]]。