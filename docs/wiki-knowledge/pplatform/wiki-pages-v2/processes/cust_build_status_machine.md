---
type: process
title: 企业建档/认证状态机（cust_company_info.cust_build_status）
page_key: cust_build_status_machine
domain: 平台内部服务对接
status: draft
aliases:
  - 建档状态
  - 认证状态机
  - cust_build_status
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[企业建档/认证状态]
  - semantic:field_semantics[cust_company_info.cust_build_status]
contract_version: "0.1"
belong: processes
---

企业从临时创建到建档成功的完整流转，由 RVS 创建、客户提交、运营中台审核三类事件驱动，并区分自主/邀请录入与简易认证两条支路。

## 需求背景

建档状态与生命周期状态分离：审核通过时除置 BUILD_SUCCESS 外还会把 cust_status 置为 EFFECT（见 [[processes/cust_status_machine]]）。不同认证方式决定提交后的落点状态与是否需要退回标记（见 [[rules/submit_cust_field_reset]]）；简易认证路径额外受 CA 开通政策约束（见 [[rules/simple_auth_ca_forbidden]]）。

## 版本演进

v0：按语义分析给出的状态与转换证据首次成页，未收录无证据的转换。

```ground:process
name: 企业建档/认证状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化（新建临时企业）
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证路径）
    source: code_enum
  - value: CUST_BUILDING
    label: 客户已提交/运营中台审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败/被拒
    source: code_enum
transitions:
  - from: INIT
    event: "RVS 调 getAndCreateTempCompany 创建临时企业"
    to: INIT
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormRvsApplication.java#getAndCreateTempCompany"
  - from: INIT
    event: "邀请认证-客户录入/注册认证提交"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#submitCust + #getCustBuildStatus(IdentifyTypeConstant.INVITE/SELF)"
  - from: INIT
    event: "邀请认证-平台录入提交"
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#submitCust + #getCustBuildStatus(IdentifyTypeConstant.INVITE_AGW)"
  - from: BUILD_FAIL
    event: "被拒后重新提交"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(条件 before==INIT||before==BUILD_FAIL && after==CUST_CONFIRM_AWAIT)"
  - from: CUST_CONFIRM_AWAIT
    event: "客户提交进入运营中台审核"
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(#updateCustBuildStatus 分支 before==CUST_CONFIRM_AWAIT && after==CUST_BUILDING)"
  - from: CUST_BUILDING
    event: "运营中台审核退回"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(分支 before==CUST_BUILDING && after==CUST_CONFIRM_AWAIT)"
  - from: CUST_BUILDING
    event: "审核通过（同时置 cust_status=EFFECT）"
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(after==BUILD_SUCCESS → custCompanyInfoService.updateById(custStatus=EFFECT))"
  - from: CUST_CONFIRM_AWAIT
    event: "平台录入客户点击确认提交"
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(IdentifyTypeConstant.INVITE_AGW 且 after==BUILD_SUCCESS)"
  - from: CUST_BUILDING
    event: "运营中台审核拒绝"
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(after==BUILD_FAIL 发送拒绝通知/短信)"
  - from: CUST_CONFIRM_AWAIT
    event: "审核拒绝"
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(after==BUILD_FAIL)"
  - from: INIT
    event: "简易认证提交"
    to: AWAIT_CUST_CONFIRM
    evidence: "code_path:CustCompanyInfoApplication.java#submitForSimpleAuth(companyInfoDO.setCustBuildStatus(AWAIT_CUST_CONFIRM))"
  - from: AWAIT_CUST_CONFIRM
    event: "客户确认（简易认证）"
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#confirmCustInfoForSimpleAuth(custCompanyInfoDao.updateStatus(custId, BUILD_SUCCESS, CustStatusEnum.EFFECT))"
```