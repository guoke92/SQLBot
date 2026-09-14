---
type: process
title: 客户建档状态机
page_key: cust_build_status
domain: 平台事件监听与同步
status: draft
aliases:
  - 企业建档状态
  - cust_build_status 流转
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
contract_version: "0.1"
belong: processes
---

描述 [[cust_company_info]] 的 `cust_build_status` 在「邀请录入 → 提交运营中台 → 审核」之间的流转，是平台侧观察建档进度的主视角。

## 需求背景

需求文档主张「企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回」，对应本状态机中 `CUST_BUILDING → BUILD_SUCCESS` 与 `CUST_BUILDING → BUILD_FAIL` 两条迁移，均由 `CustCompanyInfoApplication.updateCustBuildStatus` 承接；上游发起见 [[cust_info_sync]]。同步请求的检查状态与之对应，见 [[cust_event_check_status]]；状态变更后还联动企业/用户冻结口径，见 [[company_status_sync]]。

## 版本演进

- 简易认证路径新增 `AWAIT_CUST_CONFIRM`，且提交时强制不开通电子签章，见 [[simple_auth_no_ca]]。
- 退回（运营中台退回）回落到 `CUST_CONFIRM_AWAIT`，与「待客户确认/待提交审核」共用同一状态值，语义上偏宽。

```ground:process
name: 客户建档状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_const
  - value: BUILD_FAIL
    label: 审核拒绝/建档失败
    source: code_const
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认/待提交审核
    source: code_const
  - value: CUST_BUILDING
    label: 运营中台审核中
    source: code_const
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_const
  - value: AWAIT_CUST_CONFIRM
    label: 简易认证待确认
    source: code_const
transitions:
  - from: INIT/BUILD_FAIL
    event: 邀请认证客户录入提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify/updateCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交运营中台
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus + reqdoc:企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus + reqdoc:企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回"
```