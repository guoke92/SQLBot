---
type: rule
title: 补偿失败类型识别规则
page_key: compensation_fail_type
domain: 平台事件监听与同步
status: draft
aliases:
  - FILE_PUSH_FAIL/START_FLOW_FAIL 识别
  - 失败类型判定
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:extractFailType
  - code:RegAsyncCompensationJobHandler.java:retryCompensation
contract_version: "0.1"
belong: rules
---

失败类型由 `remark` 是否包含 `FILE_PUSH_FAIL` / `START_FLOW_FAIL` 反推定，但重试时并不按类型分派动作，而是整体重放建档异步流程。

## 需求背景

`saveCompensationRecord` 落库时以字面量拼接成 `COMPENSATION_FILE_PUSH_FAIL` / `COMPENSATION_START_FLOW_FAIL`（并非取枚举 label）。因此 [[cust_build_record]].`remark` 同时承担「筛选键」（见 [[compensation_record_filter]]）与「失败原因」两个职责。

## 版本演进

- 失败类型来自错误码常量 `PlatformEnumsExceptionEnum.FILE_PUSH_FAIL` / `START_FLOW_FAIL`，但落库为字符串拼接，枚举改名不会自动同步存量数据。
- 重试粒度为全流程，意味着类型识别只影响日志与定位，不影响行为；类型未知时直接落 FAILED，见 [[compensation_max_retry]]。

```ground:rule
name: 补偿失败类型识别
content: 按 remark 是否包含 FILE_PUSH_FAIL / START_FLOW_FAIL 判定失败类型，重试时整体重放 regAsyncService.orchestrateAsync(context)
impact: 补偿任务按失败类型定位但重试粒度为全流程
field_targets:
  - cust_build_record.remark
evidence: "code:RegAsyncCompensationJobHandler.java:extractFailType/retryCompensation"
```