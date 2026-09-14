---
type: caliber
title: 补偿重试任务状态筛选口径
page_key: compensation_retry_task_filter
domain: 平台事件监听与同步
status: draft
aliases:
  - 待重试集合
  - PENDING/RETRYING 口径
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
belong: calibers
---

`regAsyncCompensationJobHandler` 的待重试集合 = [[compensation_record_filter]] ∩ `retry_status IN ('PENDING','RETRYING')`。

## 需求背景

状态筛选保证终态（SUCCESS/FAILED）不会被再次重放；状态机见 [[cust_build_compensation_retry]]，取值见 [[cust_build_record_retry_status]]。若人工需要重放一条 FAILED 记录，必须先把状态改回 PENDING，单纯清空 `remark` 后缀无效。

## 版本演进

- 当前筛选为双状态等值集合，未按 `retryCount` 或时间窗口做二次过滤，重试节奏完全由 job 调度周期决定。

```ground:caliber
name: 补偿重试任务状态筛选
predicate: "cust_build_record.retry_status IN ('PENDING','RETRYING')"
scope: xxl-job regAsyncCompensationJobHandler 待重试集合
evidence: "code:RegAsyncCompensationJobHandler.java:getCompensationRecords"
```