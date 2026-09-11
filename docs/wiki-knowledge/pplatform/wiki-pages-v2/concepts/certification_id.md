---
type: concept
title: certificationId
page_key: concept/certification_id
domain: 微信生态/小程序/扫脸
status: draft
aliases: [认证 id]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
maps_to: "在 FaceVerifyController.faceVerifyQuery / getFaceQrCode 中为 ca_certification_info.id（Long，CFCA 一证四步链路）"
field_targets:
  - ca_certification_info.id
adjudication: boundary
also_confused_with:
  - cust_certification_info.id（低代码核查记录主键）
boundary: "凡 FaceVerifyController 入参 certificationId 均指 ca_certification_info.id，用于 updateIntentByType/mergeEmbeddedFilePath 定位行；cust_certification_info 表行通过 certification_type + ref_cust_company_info 定位，无 certificationId 入参。"
contract_version: "0.1"
---

# certificationId

在 FaceVerifyController 的刷脸链路入参中，certificationId 指 [[ca_certification_info]] 的主键 id（Long），用于 updateIntentByType / mergeEmbeddedFilePath 定位行，进而回填 [[face_scan]] 相关数据。

## 需求背景

刷脸回填需要精确定位到具体的 CA 认证行，避免与低代码核查记录行的主键混淆。

## 版本演进

v0.1 明确 certificationId 的归属表。

## 边界说明

[[cust_certification_info]] 表行通过 certification_type + ref_cust_company_info 定位，无 certificationId 入参。

相关：[[ca_certification_info]]、[[cust_certification_info]]、[[miniprogram_qrcode]]、[[face_business_no]]。