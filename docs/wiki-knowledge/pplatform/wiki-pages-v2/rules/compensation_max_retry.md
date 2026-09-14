---
type: rule
title: 补偿重试上限规则
page_key: compensation_max_retry
domain: 平台事件监听与同步
status: draft
aliases:
  - maxRetryCount 规则
  - 补偿重试上限
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
contract_version: "0.1"
belong: rules
---

重试次数达到上限后记录被标记为 FAILED 并放弃，否则重置为 PENDING 继续排队。

## 需求背景

上限默认 3。与 [[client_api_sync_error]] 的 `retry_num` 常驻 3 相互印证：两个域都采用「3 次即终止」的补偿策略，但一个用列、一个用 JSON，见 [[retry_count]]。判定时机在重试失败分支，成功分支直接落 SUCCESS，见 [[cust_build_compensation_retry]]。

## 版本演进

- 达上限时在 `remark` 追加 `_FAILED_MAX_RETRY_n`，使终态在文本层也可辨识，见 [[compensation_record_filter]]。
- 上限值来源为 `maxRetryCount` 配置，改配置会影响存量尚未终止的记录。

```ground:rule
name: 补偿重试上限规则
content: retryCount>=maxRetryCount(默认3) → markAsFailed；否则 retryStatus 重置 PENDING、retryCount+1 并写 lastRetryTime
impact: 决定补偿记录是否最终放弃
field_targets:
  - cust_build_record.retry_status
  - cust_build_record.return_data
evidence: "code:RegAsyncCompensationJobHandler.java:updateRetryCount"
```