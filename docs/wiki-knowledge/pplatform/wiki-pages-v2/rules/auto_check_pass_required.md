---
type: rule
title: 自动审核结果必须为自动认证通过才继续
page_key: auto_check_pass_required
domain: 客户中心
status: draft
aliases:
  - autoCheckMsg 阻断
  - 自动核查前置校验
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:getFaceQrCodeByCertificationNo
contract_version: "0.1"
belong: rules
---

该规则在获取人脸二维码前做前置校验：若自动核查结果不是自动认证通过，则抛出 autoCheckMsg 阻断后续流程。作用于 [[cust_certification_info]].auto_verify_status，与 [[auto_verify]] 术语及 [[face_verify_passed]] 口径相关。

```ground:rule
name: 自动审核结果必须为自动认证通过才继续
content: getFaceQrCodeByCertificationNo 中调用 verifyPersonOCR，若 autoCheckResult 不等于 AUTOMATIC_AUTHENTICATION_PASSED 则抛出 autoCheckMsg。
impact: 阻断后续人脸二维码与建档流程。
field_targets:
  - cust_certification_info.auto_verify_status
evidence: code_path:FaceVerifyController.java:getFaceQrCodeByCertificationNo
```

## 需求背景

当前语义分析未提供与本规则相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。