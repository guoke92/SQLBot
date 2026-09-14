---
type: process
title: 企业认证状态机（cust_build_status）
page_key: enterprise_auth_status_machine
domain: 企业建档与认证
status: draft
aliases:
  - 建档状态机
  - 认证状态流转
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:submitCust
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
  - code:ApplyCompanyInfoApplication.java:addCustApplyWorkFlow
  - code:CustCompanyOperationApplication.java:reAuthentication
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
belong: processes
---

本流程描述 `cust_company_info.cust_build_status`（见 [[auth_status]]）在企业建档与认证过程中的流转。该字段是**建档/认证的整体进度**，与客户生命周期状态（[[customer_status_machine]]）、运营中台单次审核状态（[[operation_check_status_machine]]）相互独立，边界见 [[customer_status]] 与 [[check_status]] 的裁定说明。

主干路径为：初始化 → 待客户确认 → 认证中 → 认证成功；分支包括认证失败后重新提交、运营退回后回到待客户确认、以及待客户确认状态下直接重置为 INIT 重新认证（受 [[reauthentication_restriction]] 约束）。平台录入（认证方式 `INVITE_AGW`）的提交会跳过“待客户确认”直接进入认证中，该差异由 [[identify_style]] 决定。认证成功是进入生效企业的必要条件之一，口径见 [[effective_company]]；相关的“认证中”“待客户确认”判断口径见 [[certifying]] 与 [[pending_customer_confirm]]。

状态更新存在并发保护约束，见 [[auth_status_conditional_update]]；认证成功会联动客户状态，见 [[auth_success_sets_customer_effective]]。

```ground:process
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
    label: 认证中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
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
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证）
    source: code_enum
  - value: CUST_AUDIT_AWAIT
    label: 审核等待
    source: db_dist
  - value: BUILDING
    label: 建档中
    source: db_dist
  - value: CUST_BUILD_SUCCESS
    label: 认证成功（历史值）
    source: db_dist
transitions:
  - from: INIT
    event: 提交建档（认证方式=INVITE或SELF）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:submitCust"
  - from: INIT
    event: 提交建档（认证方式=INVITE_AGW）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:submitCust"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CONFIRM_AWAIT
    event: 简易认证确认
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth"
  - from: BUILD_FAIL
    event: 重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:ApplyCompanyInfoApplication.java:addCustApplyWorkFlow"
  - from: CUST_CONFIRM_AWAIT
    event: 重新认证
    to: INIT
    evidence: "code_path:CustCompanyOperationApplication.java:reAuthentication"
```

## 需求背景

暂无需求文档主张。状态集合中 `CUST_AUDIT_AWAIT`、`BUILDING`、`CUST_BUILD_SUCCESS` 三个取值来源于数据库分布（`db_dist`）而非代码枚举，其中 `CUST_BUILD_SUCCESS` 被标注为历史值，说明该状态存在历史数据兼容问题，详见页末 REVIEW 说明。

## 版本演进

- v0.1：依据语义分析建立状态机页，登记 12 个状态（9 个代码枚举值 + 3 个数据库分布值）与 8 条流转及其代码证据。