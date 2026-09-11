---
type: table
title: cust_certification_info（客户核查记录表）
page_key: table/cust_certification_info
domain: 微信生态/小程序/扫脸
status: draft
aliases: [核查记录表, 认证核查表]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:AutoVerifyServiceImpl.java
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# cust_certification_info

客户核查记录表：一行代表一次「核查项」结果，核查项由 [[certification_type]] 枚举区分，覆盖企业四要素 / 二要素、法人三要素、授权人三要素、法人 OCR、授权人 OCR、营业执照 OCR、法人影音 OCR、授权人影音 OCR 与人脸核查（FACE_VERIFY）。扫脸链路通过 FACE_VERIFY 行承载，是 [[face_verify_passed]] 口径的物理落点。

## 需求背景

低代码核查引擎将 OCR、要素比对、人脸核身统一登记为核查行，自动核查与人工核查双轨并存，任一通过即视为通过，便于人工兜底。人脸核查额外落 `face_business_no`，用于按流水号回拉人脸影像文件。

## 版本演进

v0.1 记录核查项类型与结果字典取值。`auto_verify_count / manual_verify_count` 的「>=3 次」校验当前被代码注释，未生效，后续版本是否放开待定。



相关：[[cust_person_info]]、[[face_verify_passed]]、[[realname_face_verify_state]]、[[face_business_no]]、[[face_scan]]。