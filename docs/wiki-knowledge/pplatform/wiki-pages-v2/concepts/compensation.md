---
type: concept
title: 补偿
page_key: concepts/compensation
domain: 平台事件监听与同步
status: draft
aliases:
  - COMPENSATION_
  - regAsyncCompensationJobHandler
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
contract_version: "0.1"
maps_to: "建档异步流程失败后的重放补偿（RegAsyncCompensationJobHandler + RegAsyncService.saveCompensationRecord）"
field_targets:
  - cust_build_record.remark
  - cust_build_record.retry_status
  - cust_build_record.return_data
adjudication:
  kind: boundary
  boundary: "补偿以 cust_build_record.remark='COMPENSATION_'+failType 识别，状态为 retry_status；同步失败以 client_api_sync_error.enable='N' 识别。"
also_confused_with:
  - ClientApiSyncErrorDO 的同步失败重试
---

「补偿」指建档异步流程（文件推送 / 流程发起）失败后的重放机制：失败时 `RegAsyncService.saveCompensationRecord` 落一条带 `COMPENSATION_` 前缀的 [[tables/cust_build_record]] 记录并序列化重放上下文，补偿任务 `processCompensationRecord` 反序列化后重放整个异步流程。

## 需求背景
补偿需要三个要素：识别（remark 前缀 + retry_status 未终态，见 [[calibers/build-compensation-pending-records]]）、上下文（pushData 中的 RegAsyncContext）、上限（[[rules/compensation-max-retry]]）。跨租户可见性由 [[rules/compensation-tenant-context-all]] 保证。与同步失败重试的边界见 [[concepts/sync-error-record]]。

## 版本演进
- v0 契约：状态机见 [[processes/build-async-compensation-retry]]；当前 retry_status 为代码枚举，尚无 DB 实测分布。