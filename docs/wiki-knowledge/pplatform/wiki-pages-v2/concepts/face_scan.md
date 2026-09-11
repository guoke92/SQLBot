---
type: concept
title: 扫脸 / 人脸识别
page_key: concept/face_scan
domain: 微信生态/小程序/扫脸
status: draft
aliases: [H5_FACE, H5刷脸, 意愿认证, faceVerify, 刷脸]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
maps_to: "cust_certification_info.certification_type = 'FACE_VERIFY' 与 ca_certification_info.intent_h5_face_json（authType=H5_FACE）"
field_targets:
  - cust_certification_info.certification_type
  - ca_certification_info.intent_h5_face_json
adjudication: boundary
also_confused_with:
  - OCR 身份证核查（LEGAL_OCR/AUTH_OCR）
  - 三要素手机号实名（LEGAL_THREE_ELEMENTS/AUTH_THREE_ELEMENTS）
boundary: "扫脸=人脸比对（FaceVerifyController + miniFaceService），走小程序二维码；OCR/三要素属于证照识别与实名比对，同一张 cust_certification_info 表不同 certification_type 行，不可互相替代。"
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

# 扫脸 / 人脸识别

「扫脸 / 人脸识别 / H5 刷脸」是同一业务动作的不同叫法，指通过微信小程序二维码完成的人脸比对与意愿认证。它落在两处：核查记录侧为 `cust_certification_info.certification_type = FACE_VERIFY`，一证四步侧为 `ca_certification_info.intent_h5_face_json`（authType = H5_FACE）。

## 需求背景

扫脸既是核身手段也是意愿表达手段，需要与证照 OCR、三要素实名区分，避免口径混用。

## 版本演进

v0.1 建立术语边界：扫脸 ≠ OCR ≠ 三要素手机号实名。

## 边界说明

扫脸走小程序二维码与人脸比对服务；OCR / 三要素同在 [[cust_certification_info]] 表、以不同 [[certification_type]] 区分，不可互相替代。

相关：[[certification_type]]、[[miniprogram_qrcode]]、[[face_verify_passed]]、[[face_intent_subject]]、[[face_business_no]]。

相关：[[ca_certification_info]]
