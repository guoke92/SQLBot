---
type: process
title: "核查/实名认证状态机"
page_key: certification_verify_machine
domain: "customer-onboarding"
status: draft
aliases:
  - "自动核查状态机"
  - "认证核查流转"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:getFaceQrCodeByCertificationNo(autoCheckResult != AUTOMATIC_AUTHENTICATION_PASSED 抛异常)"
  - "code_path:AutoVerifyController.java:saveManual + FaceVerifyController.java:isFaceVerifyPassed"
contract_version: "0.1"
belong: processes
---

核查/实名认证状态机描述 `cust_certification_info.auto_verify_status` 的取值流转，覆盖自动核查与人工核查两条通道。这是「自动审核」一词在代码中的实际落点，与运营中台的工作流审核结论不是同一环节，边界见 [[concepts/auto_verify]] 与 [[concepts/manual_verify]]。

## 需求背景

需求文档称自动审核可自动通过准入，并可在失败时进入人工审核队列。现有代码只提供了自动核查与人工提交核查结论两个入口，未见自动写企业准入状态、也未见人工审核队列结构与消费逻辑，故相关主张在本链路中未获证实，详见 [[concepts/auto_verify]] 与 [[concepts/manual_verify]] 的版本演进说明。(document_claim，未证实)

## 版本演进

- 自动核查按 `checkType` 分支为信息核查与影像核查两条实现路径，见 [[calibers/auto_verify_type_branch]]。
- 人脸核验二维码取码前置了「自动核查未通过即抛异常」的拦截，见本页 transitions。
- 核查结果字段族（实名、人脸、手机实名）与 [[tables/cust_person_info]] 共用同一枚举族。

```ground:process
name: 核查/实名认证状态机
field: cust_certification_info.auto_verify_status
states:
  - value: "TO_BE_VERIFIED"
    label: "待核查/待认证"
    source: "code_enum"
  - value: "AUTOMATIC_AUTHENTICATION_PASSED"
    label: "自动核查通过"
    source: "code_enum"
  - value: "MANUAL_AUTHENTICATION_PASSED"
    label: "人工核查通过"
    source: "code_enum"
transitions:
  - from: "TO_BE_VERIFIED"
    event: "自动核查(OCR/人脸/影像)结果通过"
    to: "AUTOMATIC_AUTHENTICATION_PASSED"
    evidence: "code_path:AutoVerifyController.java:getFaceQrCodeByCertificationNo(autoCheckResult != AUTOMATIC_AUTHENTICATION_PASSED 抛异常)"
  - from: "TO_BE_VERIFIED"
    event: "人工审核提交(saveManual)"
    to: "MANUAL_AUTHENTICATION_PASSED"
    evidence: "code_path:AutoVerifyController.java:saveManual + FaceVerifyController.java:isFaceVerifyPassed"
```

相关：[[tables/cust_certification_info]]、[[tables/cust_person_info]]、[[concepts/auto_verify]]、[[calibers/auto_verify_type_branch]]。