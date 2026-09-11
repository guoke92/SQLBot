---
type: process
title: "企业建档认证状态机"
page_key: "processes/company_build_status_machine"
domain: "customer-onboarding"
status: draft
aliases:
  - "建档状态流转"
  - "认证状态流转"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:checkMessage"
contract_version: "0.1"
---

企业建档认证状态机描述 `cust_company_info.cust_build_status` 的取值与流转：从初始待提交，到客户确认、中台审核中，最终落到建档成功或失败；已生效企业的后续变更则进入「变更中」。该字段与单次工作流审核结论 `check_status` 不是同一维度，边界见 [[concepts/build_status]] 与 [[concepts/check_status]]。

## 需求背景

需求文档主张：企业状态流转为「待提交 → 审核中 → 已通过」，「已驳回 → 待提交」，即驳回后企业可修改信息重新提交。该主张与代码一致，代码依据为 `CustStatusCommitProcessor.java:checkMessage`：`CUST_CHECK_REJECT` 落 `BUILD_FAIL`，`CUST_CHECK_BACKTOCUSTOM` 落 `CUST_CONFIRM_AWAIT`，从而允许重新提交。

驳回后的展示口径与 [[tables/cust_company_info]] 的 `cust_build_status` 直接相关；审核通过/拒绝的落库入口切换见 [[rules/workflow_callback_routing]]。

## 版本演进

- 状态流转的原实现类 `CustStatusCommitProcessor` 已 `@Deprecated`，本页流转仅作参考，新链路以拉取式处理器为准，见 [[rules/legacy_status_processor_deprecated]] 与 [[rules/workflow_callback_routing]]。
- 平台录入（`INVITE_AGW`）存在专门的退回分支，见本页 transitions；与之对应的审核轨迹取数口径见 [[calibers/callback_audit_track_fetch]]。
- 已生效企业的「变更中」状态会阻断新的变更提交，见 [[calibers/change_in_flight_block]]。

```ground:process
name: 企业建档认证状态机
field: cust_company_info.cust_build_status
states:
  - value: "INIT"
    label: "初始/待提交"
    source: "code_enum"
  - value: "CUST_CONFIRM_AWAIT"
    label: "待客户确认"
    source: "code_enum"
  - value: "CUST_BUILDING"
    label: "认证审核中（运营中台审核）"
    source: "code_enum"
  - value: "BUILD_SUCCESS"
    label: "认证/建档成功"
    source: "code_enum"
  - value: "BUILD_FAIL"
    label: "认证/建档失败（拒绝）"
    source: "code_enum"
  - value: "CUST_CHANGE"
    label: "变更中"
    source: "code_enum"
transitions:
  - from: "CUST_CONFIRM_AWAIT"
    event: "客户提交、运营中台审核中(CUST_CHECK_CHECKING)"
    to: "CUST_BUILDING"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "运营中台退回待客户确认(CUST_CHECK_BACKTOCUSTOM)"
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "运营中台审核通过(CUST_CHECK_PASS)"
    to: "BUILD_SUCCESS"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "运营中台审核拒绝(CUST_CHECK_REJECT)"
    to: "BUILD_FAIL"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "平台录入(INVITE_AGW)审核退回待客户确认"
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
reqdoc_anchors:
  - claim: "审核驳回则企业状态置为已驳回，企业修改信息后重新提交"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage + reqdoc:company-reject-to-fail-resubmit"
  - claim: "企业状态流转：待提交 → 审核中 → 已通过；已驳回 → 待提交"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage + reqdoc:company-status-flow"
```

相关：[[tables/cust_company_info]]、[[processes/workflow_check_status_machine]]、[[concepts/build_status]]、[[calibers/effect_company]]。