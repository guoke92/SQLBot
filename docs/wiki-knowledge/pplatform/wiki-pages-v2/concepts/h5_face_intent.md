---
type: concept
title: H5刷脸意愿
page_key: h5_face_intent
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - CFCA 一证四步意愿认证
  - intent_h5_face_json
  - authType=H5_FACE
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:H5刷脸意愿"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
maps_to: ca_certification_info.intent_h5_face_json
field_targets:
  - ca_certification_info.intent_h5_face_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.intent_sms_json
  - cust_certification_info.auto_verify_status
belong: concepts
field_targets: [ca_certification_info.intent_h5_face_json]
sources: ["enrich:wiki-admin"]
---

# H5刷脸意愿

## 业务定位

指 CFCA 签章中台意愿认证中的 H5 刷脸块（`authType = H5_FACE`），以 [[tables/ca_certification_info|CFCA 认证与上送表]] 的 `intent_h5_face_json` 列承载 DBaaS 请求/响应原文，由人脸通过后在 `faceVerifyQuery` 中回填。

## 需求背景

上报报文要求意愿证据可追溯，故刷脸意愿必须与短信意愿分列留痕，且只能在 [[calibers/face_verify_passed|人脸认证通过]] 之后写入。

## 版本演进

从代码可见，回填动作绑定在 `FaceVerifyController` 的人脸通过分支上，写入口径与 [[processes/certification_verify_status|人脸/实名认证结果状态]] 的通过判断耦合。

## 边界

- H5_FACE 是签章中台意愿认证块。
- 短信意愿写 `intent_sms_json`，两者不可混用。
- 人脸核查结果写 [[tables/cust_certification_info|认证记录表]]，不是意愿块。

相关：[[ca_certification_info]]
