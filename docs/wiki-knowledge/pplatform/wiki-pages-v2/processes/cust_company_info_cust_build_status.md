---
type: process
title: 企业认证/建档状态机 (cust_company_info.cust_build_status)
page_key: cust_company_info_cust_build_status
domain: 企业变更与运营变更
status: draft
aliases: [建档状态机, cust_build_status, 重新建档状态]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustCompanyInfoApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: processes
---

本状态机描述企业客户（[[cust_company_info]]）认证/建档的流转，服务于变更项中的「重新建档」相关场景。建档成功后企业进入 `cust_status=EFFECT`，与 [[cust_company_info_cust_status]] 联动。

## 需求背景

变更项可能要求企业重新提交材料并由运营中台重新审核建档，因此需要一条独立于变更审核（[[cust_change_record_status]]）的建档状态线：客户确认 → 中台审核 → 成功/拒绝，退回时可回到待客户确认。

## 版本演进

v0.1：首次抽取五个状态与五条迁移；本页暂无历史版本差异记录。

```ground:process
name: 企业认证/建档状态机（变更项'重新建档'相关）
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_const
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_const
  - value: CUST_BUILDING
    label: 运营中台审核中
    source: code_const
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_const
  - value: BUILD_FAIL
    label: 建档拒绝
    source: code_const
transitions:
  - from: INIT/BUILD_FAIL
    event: 客户提交资料
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(before INIT|BUILD_FAIL → after CUST_CONFIRM_AWAIT)"
  - from: CUST_CONFIRM_AWAIT
    event: 推运营中台审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(before CUST_CONFIRM_AWAIT → after CUST_BUILDING)"
  - from: CUST_BUILDING
    event: 运营中台退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(before CUST_BUILDING → after CUST_CONFIRM_AWAIT)"
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(after BUILD_SUCCESS → cust_status=EFFECT)"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify(after BUILD_FAIL)"
```

相关页面：[[cust_company_info]]、[[cust_company_info_cust_status]]、[[cust_change_record_status]]。