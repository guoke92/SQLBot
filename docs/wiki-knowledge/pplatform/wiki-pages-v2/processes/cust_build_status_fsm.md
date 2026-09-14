---
type: process
title: 企业认证/建档状态机（cust_build_status）
page_key: cust_build_status_fsm
domain: 数据权限与组织
status: draft
aliases: [企业建档状态机, cust_build_status, CustBuildStatusEnum]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_company_info.cust_build_status
belong: processes
---

企业认证/建档状态机，承载于 [[tables/cust_company_info]].cust_build_status。状态取值来自代码枚举 CustBuildStatusEnum。流转的入口取决于认证方式 identify_style：邀请-客户录入（INVITE）与自主认证（SELF）提交后进入 CUST_CONFIRM_AWAIT，邀请-平台录入（INVITE_AGW）提交后直接进入 CUST_BUILDING。简易认证（SIMPLE）走独立的 AWAIT_CUST_CONFIRM 支线。

建档成功是组织根节点初始化、机构管理员绑定定时任务与企业查询前置校验的前置口径，见 [[calibers/build_success_cust]]。建档成功同时触发企业经营状态从 ADD 到 EFFECT，见 [[processes/cust_status_fsm]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustCompanyInfoApplication 相关方法。

## 版本演进

v0：依据 code 证据建模，覆盖入库、驳回重提、审核退回、审核通过、简易认证确认五类事件。

```ground:process
name: 企业认证/建档状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始/待提交
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中（运营中台）
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 审核驳回/建档失败
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 简易认证提交后的待确认
    source: code_enum
transitions:
  - from: INIT
    event: 邀请认证（客户录入）/自主认证提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#getCustBuildStatus
  - from: INIT
    event: 邀请认证-平台录入（INVITE_AGW）提交
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java#getCustBuildStatus
  - from: BUILD_FAIL
    event: 驳回后重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交，推送运营中台审核
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_BUILDING
    event: 运营中台审核退回（客户录入场景）
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_BUILDING
    event: 运营中台审核通过，流转到客户确认（平台录入场景）
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_BUILDING
    event: 认证审核通过
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 平台录入客户点击确认提交
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 认证审核拒绝
    to: BUILD_FAIL
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: INIT
    event: 简易认证提交（非建档成功、非变更）
    to: AWAIT_CUST_CONFIRM
    evidence: code_path:CustCompanyInfoApplication.java#submitForSimpleAuth
  - from: AWAIT_CUST_CONFIRM
    event: 简易认证确认（含资金方直接生效）
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java#confirmCustInfoForSimpleAuth
```