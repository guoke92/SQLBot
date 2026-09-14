---
type: process
title: "工作流审核状态机"
page_key: workflow_check_status_machine
domain: "customer-onboarding"
status: draft
aliases:
  - "审核状态流转"
  - "check_status 状态机"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process(setCheckStatus=rtfs.getCheckStaus().name())"
  - "code_path:CustStatusCommitProcessor.java:process(RtfState.getByDesc->getCheckStaus)"
  - "code_path:CustStatusCommitProcessor.java:checkMessage(CUST_CHECK_CHECKING && CUST_CONFIRM_AWAIT -> CUST_BUILDING)"
contract_version: "0.1"
belong: processes
---

工作流审核状态机描述 `cust_company_info.check_status` 的四个取值及其流转。回调侧以运营中台的 `RtfState`（中文描述，如通过/拒绝/退回客户）解读事件，落库前统一转成 `CheckStatus` 枚举名，术语映射见 [[concepts/check_status]]。本状态机与 [[processes/company_build_status_machine]] 联动：`check_status` 的结论驱动 `cust_build_status` 进度。

## 需求背景

企业准入须经运营中台工作流审核，审核「通过」后企业进入建档成功，「拒绝」后进入失败，「退回客户」则回到待客户确认并由客户修改后重新提交。这是 [[processes/company_build_status_machine]] 中需求主张在本状态机上的对应实现。

## 版本演进

- 本状态机的写入入口分两路：通过/拒绝由拉取式处理器完成，中间状态由同步事件提供者落库，见 [[rules/workflow_callback_routing]]。
- 执行器注释声称「仅处理拒绝」，但实现同时处理通过与拒绝，阅读时以代码为准，见 [[rules/workflow_processor_scope_comment_mismatch]]。
- 回调会校验统一社会信用代码一致性，不一致直接阻断，见 [[rules/social_unified_code_check]]。
- 审核轨迹（审批人）取数按 `identify_style` 分支，见 [[calibers/callback_audit_track_fetch]] 与 [[rules/audit_track_fetch]]。
- 本状态机所在的原处理器已废弃，历史流转仅供参考，见 [[rules/legacy_status_processor_deprecated]]。

```ground:process
name: 工作流审核状态机
field: cust_company_info.check_status
states:
  - value: "CUST_CHECK_CHECKING"
    label: "审核中"
    source: "code_enum"
  - value: "CUST_CHECK_BACKTOCUSTOM"
    label: "退回客户确认"
    source: "code_enum"
  - value: "CUST_CHECK_PASS"
    label: "审核通过"
    source: "code_enum"
  - value: "CUST_CHECK_REJECT"
    label: "审核拒绝"
    source: "code_enum"
transitions:
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台工作流回调 rtfState=通过(RtfState.PASS)"
    to: "CUST_CHECK_PASS"
    evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process(setCheckStatus=rtfs.getCheckStaus().name())"
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台工作流回调 rtfState=拒绝(RtfState.REJECT)"
    to: "CUST_CHECK_REJECT"
    evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台回调 rtfState=退回客户/提交客户确认（CheckStatus.CUST_CHECK_BACKTOCUSTOM）"
    to: "CUST_CHECK_BACKTOCUSTOM"
    evidence: "code_path:CustStatusCommitProcessor.java:process(RtfState.getByDesc->getCheckStaus)"
  - from: "CUST_CHECK_BACKTOCUSTOM"
    event: "客户确认后重新提交，运营中台回调 rtfState=审核中"
    to: "CUST_CHECK_CHECKING"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage(CUST_CHECK_CHECKING && CUST_CONFIRM_AWAIT -> CUST_BUILDING)"
```

相关：[[tables/cust_company_info]]、[[processes/company_build_status_machine]]、[[concepts/check_status]]、[[rules/workflow_callback_routing]]。