---
type: process
title: 建档异步补偿重试状态机
page_key: cust_build_compensation_retry
domain: 平台事件监听与同步
status: draft
aliases:
  - 补偿重试流程
  - 建档补偿状态机
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
contract_version: "0.1"
belong: processes
---

用于描述 [[cust_build_record]] 的 `retry_status` 在 xxl-job 驱动下的流转。记录由建档失败时创建为 PENDING，job 捞取后置 RETRYING，成功落 SUCCESS，失败按上限回到 PENDING 或落 FAILED。

## 需求背景

需求侧要求建档不因外部依赖（文件推送、流程拉起）失败而中断：失败即登记补偿记录并重试，重试粒度为整条 `orchestrateAsync(context)` 重放，失败类型仅用于定位，见 [[compensation_fail_type]] 与 [[compensation_max_retry]]。job 只处理 `remark LIKE 'COMPENSATION_%'` 且状态在 PENDING/RETRYING 的记录，见 [[compensation_record_filter]]。

## 版本演进

- 终态标记沿用 `remark` 追加后缀（`_RETRY_SUCCESS`、`_FAILED_MAX_RETRY_n`）的方式，`retry_status` 之外还有一层文本旁证。
- 状态取值见 [[cust_build_record_retry_status]]。

```ground:process
name: 建档异步补偿重试状态
field: cust_build_record.retry_status
states:
  - value: PENDING
    label: 待重试
    source: code_const
  - value: RETRYING
    label: 重试中
    source: code_const
  - value: SUCCESS
    label: 重试成功
    source: code_const
  - value: FAILED
    label: 重试失败/放弃
    source: code_const
transitions:
  - from: "(新建)"
    event: saveCompensationRecord
    to: PENDING
    evidence: "code_path:RegAsyncService.java:saveCompensationRecord"
  - from: PENDING
    event: xxl-job 命中补偿记录
    to: RETRYING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:processCompensationRecord(record.setRetryStatus(RETRYING))"
  - from: RETRYING
    event: retryCompensation 成功
    to: SUCCESS
    evidence: "code_path:RegAsyncCompensationJobHandler.java:handleRetrySuccess"
  - from: RETRYING
    event: 重试失败且 retryCount<maxRetryCount
    to: PENDING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:updateRetryCount(setRetryStatus(PENDING))"
  - from: RETRYING
    event: retryCount>=maxRetryCount 或类型未知
    to: FAILED
    evidence: "code_path:RegAsyncCompensationJobHandler.java:markAsFailed"
```