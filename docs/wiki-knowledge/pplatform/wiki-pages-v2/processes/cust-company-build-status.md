---
type: process
title: 企业建档状态机
page_key: cust-company-build-status
domain: 平台事件监听与同步
status: draft
aliases:
  - cust_build_status 状态机
  - CustBuildStatusEnum
  - 企业建档状态
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:submitForSimpleAuth
contract_version: "0.1"
belong: processes
---

企业建档状态机描述 `cust_company_info.cust_build_status` 的推进路径：提交建档进入待客户确认或审核中，客户提交后推送运营中台，审核通过转 BUILD_SUCCESS，退回/拒绝转 CUST_CONFIRM_AWAIT 或 BUILD_FAIL；简易认证另走 AWAIT_CUST_CONFIRM 分支。详见 [[concepts/cust-build]]。

## 需求背景
企业准入存在人工审核、驳回后可修改重新提交的流程：`messageNotify` 覆盖提交（INVITE → CUST_CONFIRM_AWAIT）、推送运营中台（CUST_CONFIRM_AWAIT → CUST_BUILDING）、退回（CUST_BUILDING → CUST_CONFIRM_AWAIT）、拒绝（CUST_CONFIRM_AWAIT → BUILD_FAIL）与驳回后重新提交。审核通过由 `updateCustBuildStatus` 落 BUILD_SUCCESS。回调侧的去重策略见 [[rules/reject-pass-callback-workflow]]，终态口径见 [[calibers/build-success-company]]。

## 版本演进
- v0 契约：状态集合取自 CustBuildStatusEnum；产融侧状态与运营中台审核状态（OperApiConstants.CheckStatus：CUST_CHECK_PASS/REJECT/INIT 等）是两套体系，通过回调对齐。
- 运营中台客户数据变动回调产融 CustEventListener 的入站链路（`CustSyncEventProvider.onEvent/custChangeBroadcast/syncOperatorUser`）在代码层已证实，是该状态机的驱动源之一。

```ground:process
name: 企业建档状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_enum
  - value: BUILD_FAIL
    label: 认证驳回/失败
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 客户已提交/运营中台审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证通过/建档成功
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证提交后）
    source: code_enum
transitions:
  - from: "(新建)"
    event: 提交建档getCustBuildStatus(INVITE_AGW→CUST_BUILDING, INVITE/SELF→CUST_CONFIRM_AWAIT)
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 信息提交 (INVITE)
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: BUILD_FAIL
    event: 驳回后重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交推送运营中台completeSpAdminNotice
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 认证审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: "(简易认证)"
    event: submitForSimpleAuth提交且非变更
    to: AWAIT_CUST_CONFIRM
    evidence: "code_path:CustCompanyInfoApplication.java:submitForSimpleAuth"
related_pages:
  - tables/cust_company_info
  - concepts/cust-build
  - calibers/build-success-company
  - rules/reject-pass-callback-workflow
```