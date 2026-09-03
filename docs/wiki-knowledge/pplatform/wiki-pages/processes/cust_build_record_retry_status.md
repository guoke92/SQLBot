---
type: process
title: cust_build_record.retry_status 状态机
page_key: cust_build_record_retry_status
domain: 异步任务与数据同步
status: published
aliases: []
oid: 1
sources: ["code_enum", "code"]
contract_version: "0.1"
field_targets: [cust_build_record.retry_status]
scope:
  databases: [lowcode_pplatform]
---

cust_build_record.retry_status 定义补偿重试状态流转。相关表：[[cust_build_record]]。

## 需求背景

建档异步补偿需要自动重试，状态机保证重试过程可追踪。

## 版本演进

v0.1 提取状态机及转换证据。

```ground:process
name: cust_build_record.retry_status
field: retryStatus
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
  - from: PENDING
    event: 处理补偿记录时先标记
    to: RETRYING
    evidence: code_path:RegAsyncCompensationJobHandler.processCompensationRecord
  - from: RETRYING
    event: retryCompensation成功
    to: SUCCESS
    evidence: code_path:RegAsyncCompensationJobHandler.handleRetrySuccess
  - from: RETRYING
    event: retryCompensation失败且未达最大次数
    to: PENDING
    evidence: code_path:RegAsyncCompensationJobHandler.updateRetryCount
  - from: RETRYING
    event: retryCompensation失败且达最大次数
    to: FAILED
    evidence: code_path:RegAsyncCompensationJobHandler.markAsFailed
```