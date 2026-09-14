---
type: process
title: 异步导入导出任务状态机
page_key: async_io_task_status
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [异步任务状态, async_io_task.status, PENDING/RUNNING/SUCCESS/FAILED]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:AsyncIoTaskManager.markRunning / markSuccessWithResult / markSuccessWithFile / markImportFailed / markRunningTimeout；AsyncIoTaskXxlJobHandler.handleFailure"
  - "db:async_io_task.status 分布（RUNNING=3）"
contract_version: "0.1"
belong: processes
---

异步导入导出任务状态机描述 `async_io_task.status` 从 PENDING 出发的四条分支：正常无流返回或带文件成功上传 COS 都进入 SUCCESS；业务抛错、导入存在失败行、以及 RUNNING 停留超过 timeoutMinutes 的兜底清理都进入 FAILED。PENDING → RUNNING 使用 CAS 更新（where status=PENDING）保证并发下只有一个执行者抢到任务。

相关口径：[[async_io_task_pending]]（分片拉取）、[[async_io_task_running]]（超时清理）、[[async_io_task_not_deleted]]（查询可见性）。

## 需求背景
文件型导入导出需要异步执行、可观测、可重试；节点被强杀或 OOM 后必须由超时兜底把悬挂任务收敛为失败，避免任务永久停在执行中。

## 版本演进
v0.1（本页）：首版契约，四态与六条迁移均来自语义分析证据；暂无历史版本记录。

```ground:process
name: 异步导入导出任务状态
field: async_io_task.status
states:
  - value: "PENDING"
    label: 待执行
    source: code_enum
  - value: "RUNNING"
    label: 执行中
    source: db_dist
  - value: "SUCCESS"
    label: 成功
    source: db_dist
  - value: "FAILED"
    label: 失败
    source: db_dist
transitions:
  - from: "PENDING"
    event: "CAS markRunning（where status=PENDING）"
    to: "RUNNING"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunning"
  - from: "RUNNING"
    event: "业务方法正常返回且无 stream"
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithResult"
  - from: "RUNNING"
    event: "业务方法返回下载字节流并上传 COS 成功"
    to: "SUCCESS"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markSuccessWithFile"
  - from: "RUNNING"
    event: "业务方法抛 Throwable（handleFailure 兜底生成错误文件）"
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java:handleFailure"
  - from: "RUNNING"
    event: "IMPORT 正常返回但存在失败行"
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markImportFailed"
  - from: "RUNNING"
    event: "RUNNING 停留超过 timeoutMinutes（节点强杀/OOM 兜底）"
    to: "FAILED"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java:markRunningTimeout"
```