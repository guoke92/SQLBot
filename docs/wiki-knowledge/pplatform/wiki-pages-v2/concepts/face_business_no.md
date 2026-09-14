---
type: concept
title: faceBusinessNo / businessNo / busiSeqNo（业务流水号）
page_key: face_business_no
domain: 微信生态/小程序/扫脸
status: draft
aliases: [业务流水号]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniFaceService.java
  - code:FaceVerifyController.java
maps_to: "cust_certification_info.face_business_no；MiniFaceService.queryResult(businessNo)；GetFaceQrCodeReqDTO.busiSeqNo"
field_targets:
  - cust_certification_info.face_business_no
adjudication: boundary
also_confused_with:
  - ca_certification_info.batch_no
boundary: "busiSeqNo 是生成二维码时组装的查询键（custId/certificationId + 日期）；faceBusinessNo 是人脸服务返回的流水号，回写时 busiSeqNo 优先取 faceResult.getFaceBusinessNo()，其次取 snapshot.getBusinessNo()；batch_no 是签章中台上送流水号，三者不同源。"
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
---

# faceBusinessNo / businessNo / busiSeqNo（业务流水号）

三个易混的流水号：busiSeqNo 是生成二维码时组装的查询键（custId/certificationId + 日期）；faceBusinessNo 是人脸服务返回的流水号，用于按流水号拉取人脸影像（A0024）；batch_no 是签章中台上送流水号（见 [[ca_certification_info]]）。

## 需求背景

刷脸回写时需要从一个流水号回查到人脸结果与影像文件，若把三者当同一标识会取错数据源。

## 版本演进

v0.1 明确三者不同源及回写优先级。

## 边界说明

回写时 busiSeqNo 优先取 faceResult.getFaceBusinessNo()，其次取 snapshot.getBusinessNo()。

相关：[[miniprogram_qrcode]]、[[face_scan]]、[[certification_id]]、[[ca_certification_info]]。

相关：[[cust_certification_info]]
