---
type: table
title: cust_build_record 企业建档异步流程补偿记录表
page_key: tables/cust_build_record
domain: 平台事件监听与同步
status: draft
aliases:
  - 建档补偿记录
  - 补偿记录
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
contract_version: "0.1"
---

cust_build_record 记录企业建档异步流程（文件推送 / 流程拉取）失败后的补偿单元。与 [[tables/client_api_sync_error]] 的「同步失败」不同，本表以 `retry_status` 表达重试状态，并用 `remark` 前缀标记记录来源，是 [[processes/build-async-compensation-retry]] 状态机的载体表。

## 需求背景
建档异步流程包含文件推送与流程发起两步，任一步失败都需要可重放：`pushData` 保存序列化后的 `RegAsyncContext`，补偿任务反序列化后重放整个异步流程；`returnData` 保存错误信息 JSON；`remark` 以 `COMPENSATION_` 前缀拼接失败类型（FILE_PUSH_FAIL / START_FLOW_FAIL）与重试结果后缀，使补偿任务可仅凭 remark 识别待处理记录（见 [[calibers/build-compensation-pending-records]]）。

## 版本演进
- v0 契约：字段语义与状态机取自代码枚举与补偿任务实现；`remark` 后缀承载重试终止原因（如 `_FAILED_MAX_RETRY_3`），属隐式格式约定，见 [[rules/compensation-max-retry]]。
- 表内字段在代码层为驼峰命名（retryStatus/returnData），状态机字段引用写作 `cust_build_record.retry_status` / `cust_build_record.return_data`，映射关系待落库脚本阶段固化。

