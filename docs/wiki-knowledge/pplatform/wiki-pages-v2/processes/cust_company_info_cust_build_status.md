---
type: process
title: 企业认证状态机（cust_company_info.cust_build_status）
page_key: processes/cust_company_info_cust_build_status
domain: 企业画像
status: draft
aliases:
  - CustBuildStatusEnum 流程
  - 企业认证状态流转
  - cust_build_status
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# 企业认证状态机（cust_company_info.cust_build_status）

该状态机描述[[tables/cust_company_info]]（企业画像 / 客户信息主表）中 `custBuildStatus` 字段（对应 `CustBuildStatusEnum`）的取值与流转。它是「企业从录档到认证成功」的主干流程，共 7 个状态。

流转的主干有两条入口路径：`INIT` 在「邀请认证-客户录入／注册认证提交」下进入 `CUST_CONFIRM_AWAIT`（待客户确认），在「邀请认证-平台录入提交」下直接进入 `CUST_BUILDING`（审核中）。此后 `CUST_CONFIRM_AWAIT` 与 `CUST_BUILDING` 之间可因「客户提交运营中台审核」与「运营中台审核退回」双向往返；审核通过进入 `BUILD_SUCCESS`，审核拒绝进入 `BUILD_FAIL`。被驳回后的「修改后重新提交」会回到 `CUST_CONFIRM_AWAIT`。

简易认证是独立分支：状态停在 `AWAIT_CUST_CONFIRM`（待客户确认，简易认证）时，由 `confirmCustInfoForSimpleAuth` 一次确认直接进入 `BUILD_SUCCESS`。认证成功之后，企业发起变更会进入 `CUST_CHANGE`（企业变更中），该判定来自 `CustCompanyIfoEnchanceService.isNeedMiniAuth`。

需要注意本状态机与[[processes/cust_company_info_cust_status]]的耦合：认证成功是客户状态从 `ADD` 走向 `EFFECT` 的前提，而两者共同参与[[calibers/company_effect]]的四条件合取。

## 需求背景

本分析未提供该状态机的需求文档（reqdoc_claims）证据，状态与迁移均以 `CustCompanyInfoApplication` / `CustCompanyIfoEnchanceService` 代码证据为准。待业务补充：`CUST_CHANGE` 的退出路径（变更完成／失败后的目标状态）在本分析给出的代码证据中尚未出现。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:process
name: 企业认证状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始/待提交
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证）
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
    source: code_enum
  - value: BUILD_FAIL
    label: 认证失败/驳回
    source: code_enum
  - value: CUST_CHANGE
    label: 企业变更中
    source: code_enum
transitions:
  - from: INIT
    event: 邀请认证-客户录入/注册认证提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:getCustBuildStatus
  - from: INIT
    event: 邀请认证-平台录入提交
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:getCustBuildStatus
  - from: BUILD_FAIL
    event: 修改后重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交运营中台审核
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: AWAIT_CUST_CONFIRM
    event: 简易认证确认
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
  - from: BUILD_SUCCESS
    event: 企业发起变更
    to: CUST_CHANGE
    evidence: code_path:CustCompanyIfoEnchanceService.java:isNeedMiniAuth
```

相关页面：[[tables/cust_company_info]]、[[processes/cust_company_info_cust_status]]、[[concepts/company_profile]]、[[calibers/company_effect]]。