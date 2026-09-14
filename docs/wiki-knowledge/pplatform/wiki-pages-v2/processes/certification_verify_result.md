---
type: process
title: 自动/人工认证结果状态机
page_key: certification_verify_result
domain: 客户中心
status: draft
aliases:
  - 核查结果流转
  - 自动人工认证流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:isFaceVerifyPassed
  - code_path:CustPersonApplication.java:updateVerifyNameStatus
contract_version: "0.1"
belong: processes
---

自动/人工认证结果状态机描述 [[cust_certification_info]] 的 auto_verify_status 与 manual_verify_status 从待认证到通过的流转，是 [[auto_verify]] 术语的落地过程。状态来源为 CustCertificationResultTypeEnum（code_const）。

```ground:process
name: 自动/人工认证结果状态机
field: cust_certification_info.auto_verify_status / cust_certification_info.manual_verify_status
states:
  - value: TO_BE_VERIFIED
    label: 待认证
    source: code_const
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动认证通过
    source: code_const
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工认证通过
    source: code_const
transitions:
  - from: TO_BE_VERIFIED
    event: 自动核查通过
    to: AUTOMATIC_AUTHENTICATION_PASSED
    evidence: code_path:FaceVerifyController.java:isFaceVerifyPassed
  - from: TO_BE_VERIFIED
    event: 人工审核通过
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: code_path:CustPersonApplication.java:updateVerifyNameStatus
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。