---
type: caliber
title: 补偿记录筛选口径
page_key: compensation_record_filter
domain: 平台事件监听与同步
status: draft
aliases:
  - COMPENSATION_ 前缀筛选
  - 补偿记录识别
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
belong: calibers
---

xxl-job 从 [[cust_build_record]] 中捞取补偿记录时，以 `remark` 前缀 `COMPENSATION_` 作为唯一识别条件。

## 需求背景

`remark` 同时承载失败标记与终态后缀（`_RETRY_SUCCESS`、`_FAILED_MAX_RETRY_n`），因此只能用前缀匹配而不能用等值匹配；带后缀的历史记录仍会被捞出，是否重试再交给状态口径判断，见 [[compensation_retry_task_filter]]。

## 版本演进

- 失败类型由 `remark` 中的 `FILE_PUSH_FAIL` / `START_FLOW_FAIL` 反推，见 [[compensation_fail_type]]；这意味着新增失败类型必须同步维护该前缀约定。

```ground:caliber
name: 补偿记录筛选
predicate: "cust_build_record.remark LIKE 'COMPENSATION_%'"
scope: xxl-job 只处理 remark 以 COMPENSATION_ 开头的记录
evidence: "code:RegAsyncCompensationJobHandler.java:getCompensationRecords"
```