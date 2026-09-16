---
type: process
title: 企业认证状态机
page_key: cust_build_status_flow
domain: 企业建档与认证状态机
status: draft
aliases: [建档状态流转]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustCompanyInfoApplication.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [cust_company_info.cust_build_status]
---

作用于 [[cust_company_info]] 的 `cust_build_status`（字典 [[cust_build_status]]）。从 `INIT` 走出的分叉由 [[identify_style]] 决定。与企业生效状态 [[cust_status_flow]] 是两条轨道。

下面迁移边来自 `CustCompanyInfoApplication`。其余枚举值（退回、待激活、变更等）见字典页；`AWAIT_CUST_CONFIRM` 有定义，当前证据没有迁入/迁出边。

```ground:process
name: 企业认证状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户认证
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
    source: code_enum
  - value: BUILD_FAIL
    label: 认证失败
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认
    source: code_enum
transitions:
  - from: INIT
    event: 提交建档（邀请认证-客户录入/注册认证）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 提交建档（邀请认证-平台录入）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: BUILD_FAIL
    event: 重新提交（客户录入）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
```
