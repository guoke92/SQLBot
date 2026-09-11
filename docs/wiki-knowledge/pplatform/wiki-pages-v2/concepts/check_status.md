---
type: concept
title: "审核状态"
page_key: "concepts/check_status"
domain: "customer-onboarding"
status: draft
aliases:
  - "check_status"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process(setCheckStatus=rtfs.getCheckStaus().name())"
  - "code_path:CustStatusCommitProcessor.java:changeMessage"
contract_version: "0.1"
maps_to: "OperApiConstants.RtfState.getCheckStaus().name() → OperApiConstants.CheckStatus"
field_targets:
  - "cust_company_info.check_status"
  - "cust_change_record.status"
adjudication: "synonym"
also_confused_with:
  - "变更记录 cust_change_record.status"
boundary: "回调解读用 RtfState（中文描述，如 通过/拒绝/退回客户），落库前统一转 CheckStatus 枚举名；cust_change_record.status 在退回场景还会写入 returnCust-时间 的非枚举值。"
---

「审核状态」指工作流审核的结论枚举。回调报文里的状态是运营中台的 `RtfState`（中文描述），落库前统一转换为 `CheckStatus` 枚举名，因此同一结论在链路上有两套表述。主表落点见 [[tables/cust_company_info]]，状态机见 [[processes/workflow_check_status_machine]]。

## 边界

`boundary`：回调解读用 `RtfState`（中文描述，如 通过/拒绝/退回客户），落库前统一转 `CheckStatus` 枚举名；`cust_change_record.status` 在退回场景还会写入 `returnCust-时间` 的非枚举值。

因此对变更记录做枚举统计时，必须显式处理动态退回值，见 [[processes/change_record_check_machine]] 与 [[tables/cust_change_record]]。本概念与 [[concepts/build_status]] 是不同维度，两者通过流转联动。

## 需求背景

需求文档中的「审核中 / 已通过 / 已驳回」在本域对应的落库值分别是 `CUST_CHECK_CHECKING`、`CUST_CHECK_PASS`、`CUST_CHECK_REJECT`；「退回」对应 `CUST_CHECK_BACKTOCUSTOM`。

## 版本演进

- 通过/拒绝与中间状态分属两条落库通道，见 [[rules/workflow_callback_routing]]。
- 执行器对该状态的处理范围与注释不一致，见 [[rules/workflow_processor_scope_comment_mismatch]]。