---
type: process
title: 建档异步流程补偿重试状态机
page_key: processes/build-async-compensation-retry
domain: 平台事件监听与同步
status: draft
aliases:
  - retry_status 状态机
  - 补偿重试状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:handleRetrySuccess
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
  - code:RegAsyncCompensationJobHandler.java:markAsFailed
contract_version: "0.1"
---

该状态机描述建档异步流程失败记录（[[tables/cust_build_record]]）在补偿任务下的生命周期：新建即 PENDING，被扫描后进入 RETRYING，重放成功转 SUCCESS，失败则视重试次数回置 PENDING 或终态 FAILED。它是 [[concepts/compensation]] 的可执行细化。

## 需求背景
建档异步流程（文件推送 / 流程发起）失败不能只留错误日志，需要「可重放 + 有上限 + 有终态」：`saveCompensationRecord` 落 PENDING 并序列化 `RegAsyncContext`；补偿任务 `processCompensationRecord` 反序列化重放 `orchestrateAsync`；重试上限控制见 [[rules/compensation-max-retry]]，扫描可见性控制见 [[rules/compensation-tenant-context-all]]。

## 版本演进
- v0 契约：状态与迁移取自代码枚举与补偿任务实现，未引入 DB 实测；终态失败原因以 remark 后缀承载（如 `_FAILED_MAX_RETRY_3`）。
- 与 [[processes/cust-company-build-status]] 的区分：本状态机关注「失败后的技术重试」，企业建档状态机关注「业务审核推进」，两者通过 custId 关联但不共享状态字段。

```ground:process
name: 建档异步流程补偿重试状态机
field: cust_build_record.retry_status
states:
  - value: PENDING
    label: 待重试
    source: code_enum
  - value: RETRYING
    label: 重试中
    source: code_enum
  - value: SUCCESS
    label: 重试成功
    source: code_enum
  - value: FAILED
    label: 重试失败
    source: code_enum
transitions:
  - from: "(新建)"
    event: 文件推送/流程拉取失败saveCompensationRecord
    to: PENDING
    evidence: "code_path:RegAsyncService.java:saveCompensationRecord"
  - from: PENDING
    event: 补偿任务识别并开始处理processCompensationRecord
    to: RETRYING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:processCompensationRecord"
  - from: RETRYING
    event: retryCompensation重放orchestrateAsync成功handleRetrySuccess
    to: SUCCESS
    evidence: "code_path:RegAsyncCompensationJobHandler.java:handleRetrySuccess"
  - from: RETRYING
    event: 重试失败但未达最大重试次数updateRetryCount
    to: PENDING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:updateRetryCount"
  - from: RETRYING
    event: 重试次数>=maxRetryCount markAsFailed(MAX_RETRY_n)
    to: FAILED
    evidence: "code_path:RegAsyncCompensationJobHandler.java:updateRetryCount"
  - from: RETRYING
    event: 失败类型未知/无法解析markAsFailed
    to: FAILED
    evidence: "code_path:RegAsyncCompensationJobHandler.java:markAsFailed"
related_pages:
  - tables/cust_build_record
  - calibers/build-compensation-pending-records
  - rules/compensation-max-retry
```