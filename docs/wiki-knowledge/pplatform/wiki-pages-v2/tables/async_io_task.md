---
type: table
title: async_io_task（异步导入导出任务表）
page_key: table.async_io_task
domain: 租户配置
status: draft
aliases:
  - async_io_task
  - 异步任务表
  - 导入导出任务表
oid: 1
scope:
  databases:
    - lowcode-pplatform-customer-management
sources:
  - db:async_io_task
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/service/AsyncIoTaskManager.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/asyncio/job/AsyncIoTaskXxlJobHandler.java
contract_version: "0.1"
---

async_io_task 记录异步导入/导出任务的执行载体与结果产物，是租户侧批量数据操作（导入配置、导出清单等）的统一任务台账。任务通过 XXL-Job 分片广播被拉取执行，拉取口径见 [[calibers/pending_task_shard]]；任务状态机见 [[processes/async_io_task_status]]。`file_url` 的语义随状态变化：成功时是结果文件下载地址，失败时是错误文件下载地址。软删除使用字符串 `0/1`，见 [[concepts/is_deleted]]。

## 需求背景

大文件导入导出不能在同步请求内完成，因此引入任务表 + 调度器模式：调度抢到任务后以 CAS 方式置为 RUNNING，执行结束后按结果写 SUCCESS 或 FAILED，并回填结果文件地址或结果 JSON。导入部分失败时业务仍正常返回，但任务被判定为 FAILED，以便运营重试。

## 版本演进

v0.1：依据当前语义分析快照（代码枚举 + DB 取值分布）建立字段语义基线。

```yaml
table: async_io_task
fields:
  - name: status
    meaning: 异步导入导出任务状态，代码枚举 PENDING/RUNNING/SUCCESS/FAILED，实测含 SUCCESS/RUNNING/FAILED
    evidence: code
  - name: task_type
    meaning: 任务类型 IMPORT/EXPORT
    evidence: code
  - name: is_deleted
    meaning: 软删除标记：0=否 1=是
    evidence: code
  - name: file_url
    meaning: 成功=结果文件下载地址；失败=错误文件下载地址
    evidence: code
  - name: task_no
    meaning: 任务号，DB 自增，用于分片 MOD(task_no, shardTotal)=shardIndex
    evidence: code
```

相关页面：[[processes/async_io_task_status]]、[[calibers/not_deleted_async_task]]、[[calibers/pending_task_shard]]、[[concepts/is_deleted]]。