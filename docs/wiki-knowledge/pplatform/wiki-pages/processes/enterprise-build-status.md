---
type: process
title: 企业建档状态机
page_key: enterprise-build-status
belong: processes
domain: AMS联系人第三方对接
status: published
aliases: [企业建档流程, 建档状态]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

企业建档状态机描述企业从初始化、待客户确认、建设中、建档成功/失败、变更中的完整流程。

## 需求背景
企业建档流程由提交、客户确认、审核回调等事件驱动，涉及 submitCust、addCustApplyWorkFlow、messageNotify 等代码路径。AMS 联系人第三方对接时需关注企业建档状态对联系人管理的影响。

## 版本演进
初始版本基于代码枚举和迁移逻辑提取。状态包含 CUST_CONFIRM_AWAIT 和 AWAIT_CUST_CONFIRM，对应不同确认阶段。

```ground:process
name: 企业建档状态机
field: CustCompanyInfoDO.custBuildStatus
states:
  - value: INIT
    label: 初始化
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 客户建设中/审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败
    source: code_enum
  - value: CUST_CHANGE
    label: 变更中
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认(简易)
    source: code_enum
transitions:
  - from: INIT
    event: submit
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.submitCust / addCustApplyWorkFlow"
  - from: BUILD_FAIL
    event: resubmit
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.submitCust"
  - from: CUST_CONFIRM_AWAIT
    event: customerSubmit
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.messageNotify"
  - from: CUST_BUILDING
    event: auditBack
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.messageNotify"
  - from: CUST_BUILDING
    event: auditPass
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.messageNotify"
  - from: CUST_BUILDING
    event: auditReject
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.messageNotify"
```

[[cust_company_info_do]] [[enterprise_status]]