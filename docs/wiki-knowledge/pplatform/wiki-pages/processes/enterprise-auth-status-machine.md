---
type: process
title: 企业认证状态机
page_key: enterprise-auth-status-machine
domain: 企业建档与准入
status: published
aliases: [认证流程状态机, cust_build_status状态机]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 企业认证状态机

本状态机跟踪 `cust_company_info.cust_build_status` 的认证流程阶段，覆盖邀请认证、自主注册、简易认证等入口从初始化到认证通过/失败的全过程。代码枚举值包括 INIT、CUST_CONFIRM_AWAIT、CUST_BUILDING、BUILD_SUCCESS、BUILD_FAIL、BUILD_BACK、BUILD_ACTIVATE、CUST_CHANGE，数据库分布中还存在 AWAIT_CUST_CONFIRM、BUILDING、CUST_AUDIT_AWAIT、CUST_BUILD_SUCCESS 等冗余值。

## 需求背景

需求文档中“企业状态流转：待提交 → 审核中 → 已通过；已驳回 → 待提交；已通过 → 已冻结/已注销”与实际状态值 INIT/CUST_CONFIRM_AWAIT/CUST_BUILDING/BUILD_SUCCESS/BUILD_FAIL/FREEZE/WRITEOFF 名称不一致，该差异为散文性记录。状态机事件包括提交建档、客户确认提交、审核退回、审核通过、审核拒绝、重新提交等。

## 版本演进

本状态机证据来自 `ApplyCompanyInfoApplication.addCustApplyWorkFlow`、`CustCompanyInfoApplication.submitCust`、`CustCompanyInfoApplication.messageNotify/updateCustBuildStatus`、`ApplyCompanyInfoApplication.whenBuildSuccess`、`ApplyCompanyInfoApplication.whenBuildFail` 等代码路径。

```ground:state_machine
name: 企业认证状态机
field: cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证通过
    source: code_enum
  - value: BUILD_FAIL
    label: 认证失败
    source: code_enum
  - value: BUILD_BACK
    label: 退回
    source: code_enum
  - value: BUILD_ACTIVATE
    label: 待激活
    source: code_enum
  - value: CUST_CHANGE
    label: 变更中
    source: db_dist
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证）
    source: db_dist
  - value: BUILDING
    label: 审核中（冗余值）
    source: db_dist
  - value: CUST_AUDIT_AWAIT
    label: 待审核（冗余值）
    source: db_dist
  - value: CUST_BUILD_SUCCESS
    label: 认证成功（冗余值）
    source: db_dist
transitions:
  - from: INIT
    event: 提交建档（邀请认证客户录入）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:ApplyCompanyInfoApplication.addCustApplyWorkFlow 初始提交分支直接 setCustbuildStatusConfirmAwait"
  - from: INIT
    event: 提交建档（邀请认证平台录入）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.submitCust getCustBuildStatus 返回 CUST_BUILDING 用于 INVITE_AGW"
  - from: INIT
    event: 提交建档（自主注册）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.submitCust getCustBuildStatus 返回 CUST_CONFIRM_AWAIT 用于 SELF"
  - from: CUST_CONFIRM_AWAIT
    event: 客户确认提交
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.submitCust 流程中 before==CUST_CONFIRM_AWAIT && after==CUST_BUILDING 分支"
  - from: CUST_BUILDING
    event: 审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.messageNotify/updateCustBuildStatus 中 before==CUST_BUILDING && after==CUST_CONFIRM_AWAIT"
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:ApplyCompanyInfoApplication.whenBuildSuccess"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:ApplyCompanyInfoApplication.whenBuildFail"
  - from: BUILD_FAIL
    event: 重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:ApplyCompanyInfoApplication.addCustApplyWorkFlow 条件中允许 BUILD_FAIL 重新发起流程"
```

相关表：[[cust_company_info]]；相关口径：[[authenticated-company]]、[[in-transit-process]]
---REVIEW: process | 企业认证状态机---
需求文档主张“自动审核规则：企业征信评分 >= 60分，法人无不良信用记录，企业经营正常，行业不在黑名单”，代码中仅调用 `AutoVerifyService.asyncAuthCheck`，具体规则未在给定代码中实现。该主张在本次证据范围内未被覆盖，标记为待确认。
---END REVIEW---