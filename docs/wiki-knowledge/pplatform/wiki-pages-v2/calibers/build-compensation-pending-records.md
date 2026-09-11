---
type: caliber
title: 建档异步补偿待处理记录
page_key: calibers/build-compensation-pending-records
domain: 平台事件监听与同步
status: draft
aliases:
  - 补偿扫描口径
  - COMPENSATION_ 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
---

补偿任务的取数口径：仅扫描 remark 以 `COMPENSATION_` 开头且 retry_status 处于 PENDING/RETRYING 的 [[tables/cust_build_record]] 记录。

## 需求背景
建档异步流程失败记录与普通建档记录同表存放，靠 `remark` 前缀区分身份；再叠加未终态过滤，避免把 SUCCESS/FAILED 记录重复拉入重试。任务侧另按 custId / failType / 时间范围做附加过滤，并按 [[rules/compensation-tenant-context-all]] 以 `dbTenantCode='all'` 全量扫描。

## 版本演进
- v0 契约：口径取自 `RegAsyncCompensationJobHandler.getCompensationRecords`；`remark` 后缀格式（失败类型与重试结果）属隐式约定。

```ground:caliber
name: 建档异步补偿待处理记录
predicate: "cust_build_record.remark LIKE 'COMPENSATION_%' AND cust_build_record.retry_status IN ('PENDING','RETRYING')"
scope: 补偿任务扫描口径；additional过滤 custId/failType/时间范围
evidence: code
related_pages:
  - tables/cust_build_record
  - processes/build-async-compensation-retry
  - rules/compensation-tenant-context-all
```