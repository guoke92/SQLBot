---
type: process
title: 实名/人脸核查结果状态
page_key: process/realname_face_verify_state
domain: 微信生态/小程序/扫脸
status: draft
aliases: [核查结果状态, 人脸核查状态]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:AutoVerifyServiceImpl.java
contract_version: "0.1"
---

# 实名/人脸核查结果状态

描述核查结果在自动核查与人工核查双轨下的取值与流转，作用于 [[cust_certification_info]] 的 auto/manual_verify_status，以及 [[cust_person_info]] 的 face_status / phone_realname_status。

## 需求背景

自动核查失败时需支持人工复核兜底；同时人脸回写要兼顾手机号实名与刷脸两个来源。`verifyFlag=YES` 且自动失败时提前返回，避免重复走三要素链路。

## 版本演进

v0.1 记录三种结果状态与四条迁移路径。

```ground:process
state_machine: 实名/人脸核查结果状态
field: cust_certification_info.auto_verify_status / manual_verify_status / cust_person_info.face_status / cust_person_info.phone_realname_status
states:
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动核查通过
    source: code_enum
  - value: AUTOMATIC_AUTHENTICATION_FAILED
    label: 自动核查不通过
    source: code_enum
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工核查通过
    source: code_enum
transitions:
  - from: "(新建)"
    event: verifyThree 落实名三要素结果
    to: AUTOMATIC_AUTHENTICATION_PASSED / FAILED
    evidence: code_path:AutoVerifyServiceImpl.java#verifyThree
  - from: "(新建)"
    event: finishedVerifyFace 拉小程序人脸结果回写 face_status + phone_realname_status
    to: AUTOMATIC_AUTHENTICATION_PASSED / FAILED
    evidence: code_path:AutoVerifyServiceImpl.java#finishedVerifyFace
  - from: AUTOMATIC_AUTHENTICATION_FAILED
    event: saveManual 人工核查
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: code_path:AutoVerifyServiceImpl.java#saveManual
  - from: 任意
    event: verifyFlag=YES 且自动失败 → 提前 return，不继续走三要素
    to: AUTOMATIC_AUTHENTICATION_FAILED
    evidence: code_path:AutoVerifyServiceImpl.java#verifyThree
```

相关：[[cust_certification_info]]、[[cust_person_info]]、[[face_verify_passed]]、[[face_scan]]。