---
type: concept
title: 线下电子授权书
page_key: concept.offline_electronic_auth
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子签约版授权书
  - OfflineElectronicAuth
oid: 1
scope:
  databases: [unknown]
sources:
  - code:ElectronicAuthLetterApplication.java
  - code:CustAuthSignOrchestrationApplication.java
  - db:tenant_setting_config
contract_version: "0.1"
maps_to: "预览接口生成的 OfflineElectronicAuth ON_LINE 合同，由 custDocFacade.signOfflineElectronicAuthAndUpload 签署并上传影像 A0050；是否启用由 tenant_setting_config.generate_electronic_auth_flag 控制"
field_targets:
  - tenant_setting_config.generate_electronic_auth_flag
adjudication: boundary
also_confused_with:
  - authorization_agreement 授权记录
  - 线下纸质授权书（现网 OFF_AUTH 直接跳过签署）
boundary: "开关为 N 时该方法直接返回 true（保持现网线下纸质行为），不会产生电子合同"
sources: ["enrich:wiki-admin"]
---

「线下电子授权书」指线下授权场景中由系统生成、电子签章并上传影像的那份文件（`OfflineElectronicAuth`，`ON_LINE` 合同）。启用前提是租户开关 `generate_electronic_auth_flag='Y'`，见 [[rules/tenant-switch-off-legacy-behavior]]；触发条件见 [[calibers/offline-electronic-auth-trigger]]，幂等控制见 [[rules/sign-idempotency-and-lock]]。

与 [[concepts/authorization-agreement]] 的边界：本术语关注文件的生成、签署与影像上传；授权记录只表达授权状态。与「线下纸质授权书」的边界在于开关未开启时流程直接返回成功、不产生任何电子合同，即保持现网行为。

## 需求背景
线下签署的授权书需要电子化，以便留痕与归档；但电子化必须可灰度、可回退，因此文件生成与签署被包裹在租户开关与前置条件判定之后。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

相关：[[tenant_setting_config]]
