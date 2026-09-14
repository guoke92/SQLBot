---
type: concept
title: 小程序二维码
page_key: miniprogram_qrcode
domain: 微信生态/小程序/扫脸
status: draft
aliases: [getFaceQrCode, getCustBuildQrCode, 二维码]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniFaceService.java
  - code:FaceVerifyController.java
maps_to: "MiniFaceService.getFaceQrCode（扫脸/建档场景）与 MiniFaceService.getCustBuildQrCode（建档场景）"
adjudication: boundary
also_confused_with:
  - CA 关联的 certificationId 生成的二维码
boundary: "当传 certificationId 时 busiSeqNo=certificationId+LocalDate.now()，否则 busiSeqNo=custId+LocalDate.now()；busiSeqNo 语义随入参改变，是同一接口内的分支语义，不是同一个业务标识。"
contract_version: "0.1"
belong: concepts
---

# 小程序二维码

小程序二维码用于扫脸 / 建档场景，由 MiniFaceService 生成：getFaceQrCode（扫脸 / 建档）与 getCustBuildQrCode（建档）。二维码内承载 busiSeqNo 查询键。

## 需求背景

扫码刷脸需一个可回查的查询键，busiSeqNo 依据入参不同而产生分支语义。

## 版本演进

v0.1 明确 busiSeqNo 的分支语义，避免被当作同一业务标识。

## 边界说明

当传 certificationId 时 busiSeqNo=certificationId+LocalDate.now()，否则 busiSeqNo=custId+LocalDate.now()。

相关：[[face_scan]]、[[face_business_no]]、[[certification_id]]、[[face_intent_subject]]。