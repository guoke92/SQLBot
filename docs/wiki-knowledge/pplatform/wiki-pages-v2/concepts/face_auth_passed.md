---
type: concept
title: 人脸认证通过（术语）
page_key: face_auth_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 核查通过
  - automatic passed
  - manual passed
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:人脸认证通过"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
maps_to: cust_certification_info.auto_verify_status
field_targets:
  - cust_certification_info.auto_verify_status
  - cust_certification_info.manual_verify_status
adjudication: boundary
also_confused_with:
  - cust_certification_info.manual_verify_status
  - cust_person_info.phone_realname_status
belong: concepts
field_targets: [cust_certification_info.auto_verify_status]
sources: ["enrich:wiki-admin"]
---

# 人脸认证通过（术语）

## 业务定位

口头语「核查通过 / 人脸通过」在库内有两条落点：自动通过写 `auto_verify_status`，人工通过写 `manual_verify_status`。查询判定使用二者并集，见 [[calibers/face_verify_passed|人脸认证通过]]。

## 需求背景

业务方常以「人脸认证通过」同时指代自动与人工两种来源，取数时必须明确落到哪一列，避免只查 `auto_verify_status` 而漏掉人工兜底通过的记录。

## 版本演进

从代码可见，自动核查与人工核查由不同方法写入（`saveOrUpdate` / `saveManual`），状态取值见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。

## 边界

- 自动通过：`cust_certification_info.auto_verify_status`。
- 人工通过：`cust_certification_info.manual_verify_status`，见 [[calibers/manual_verify_passed|人工认证通过]]。
- 联系人手机号实名写 [[tables/cust_person_info|联系人表]] 的 `phone_realname_status`，与本术语不同层。

相关：[[cust_certification_info]]
