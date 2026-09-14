---
type: concept
title: 扫脸
page_key: saolian
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人脸认证
  - 人脸识别
  - H5刷脸
  - CFCA H5_FACE
  - 意愿认证H5_FACE
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:扫脸"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
contract_version: "0.1"
maps_to: cust_certification_info.certification_type='FACE_VERIFY'
field_targets:
  - cust_certification_info.certification_type
adjudication: boundary
also_confused_with:
  - cust_certification_info.auto_verify_status
  - ca_certification_info.intent_h5_face_json
belong: concepts
sources: ["enrich:wiki-admin"]
---

# 扫脸

## 业务定位

「扫脸」在本域内指意愿认证/活体人脸链路，落点为认证类型 `FACE_VERIFY` 的认证记录，随企业一证四步链路把 H5 刷脸意愿数据上报签章中台。参见 [[tables/cust_certification_info|认证记录表]]、[[tables/ca_certification_info|CFCA 认证与上送表]]。

## 需求背景

小程序/H5 刷脸是 CFCA 一证四步中的意愿认证环节，必须与核查结果、上报报文块区分清楚，否则会出现「以核查状态代替意愿证据」的取数错误。

## 版本演进

从代码可见，扫脸链路与实名核查链路共用联系人表与认证记录表，但语义不同：前者产出意愿块，后者产出核查状态。

## 边界

- 扫脸（`certification_type = FACE_VERIFY`）是意愿/活体链路。
- `auto_verify_status` 是核查结果状态，见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。
- `intent_h5_face_json` 是 CFCA 上报意愿块，见 [[concepts/h5_face_intent|H5刷脸意愿]]。
- 三者不等同于实名认证结果。

相关：[[cust_certification_info]]
