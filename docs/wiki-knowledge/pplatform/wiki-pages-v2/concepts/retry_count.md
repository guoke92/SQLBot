---
type: concept
title: 重试次数
page_key: retry_count
domain: 平台事件监听与同步
status: draft
aliases:
  - retryNum
  - retryCount
  - 重试计数
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
contract_version: "0.1"
maps_to: client_api_sync_error.retry_num
field_targets:
  - client_api_sync_error.retry_num
  - cust_build_record.return_data
adjudication: boundary
also_confused_with:
  - cust_build_record.return_data
belong: concepts
field_targets: [client_api_sync_error.retry_num]
---

「重试次数」在本主题内有两个完全不同的落点，同名不同形，是排查时的头号陷阱。

## 需求背景

[[client_api_sync_error]] 用独立列 `retry_num` 记录已重试次数，实测存量常驻 3（达最大重试上限）；[[cust_build_record]] 没有独立列，补偿重试次数塞在 `return_data` JSON 的 `retryCount` 字段里，与 `lastRetryTime` 一起由补偿任务维护。上限判定见 [[compensation_max_retry]]。

## 版本演进

- 两个域各自演化：同步失败表用列 + 启用标识表达终态（见 [[sync_error_retained_scope]]），补偿表用状态列 + JSON 计数表达终态（见 [[cust_build_compensation_retry]]）。
- 口径建议：按代码名 `retryNum` 检索时只查 `client_api_sync_error`，按 `retryCount` 检索时只查 `cust_build_record.return_data`，不要跨表合并统计。