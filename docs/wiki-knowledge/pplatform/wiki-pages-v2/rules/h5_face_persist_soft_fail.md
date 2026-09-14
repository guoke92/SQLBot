---
type: rule
title: H5 刷脸落库弱失败
page_key: h5_face_persist_soft_fail
domain: 微信生态/小程序/扫脸
status: draft
aliases: [刷脸落库弱失败, 静默落库]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
contract_version: "0.1"
belong: rules
---

# H5 刷脸落库弱失败

persistH5FaceIntentIfPassed 中，updateIntentByType / mergeEmbeddedFilePath 异常仅记 error 日志，不抛出，不阻断 faceVerifyQuery 返回人脸结果；未传 certificationId、人脸未通过、快照缺失均直接跳过回填。

## 需求背景

主链路可用性优先于落库完整性，落库失败不应影响用户拿到刷脸结果，代价是需靠日志审计静默缺失。

## 版本演进

v0.1 记录弱失败策略与跳过条件。

```ground:rule
name: H5 刷脸落库弱失败
content: "persistH5FaceIntentIfPassed 中 updateIntentByType / mergeEmbeddedFilePath 异常仅 error 日志，不抛出，不阻断 faceVerifyQuery 返回人脸结果；未传 certificationId、人脸未通过、快照缺失（snapshot 为空或 !isCaptured）均直接跳过回填。"
impact: "主链路可用性优先；代价是落库可能静默缺失，需靠日志审计。"
field_targets:
  - ca_certification_info.intent_h5_face_json
  - ca_certification_info.file_refs_json
evidence: code_path:FaceVerifyController.java#persistH5FaceIntentIfPassed
```

相关：[[face_verify_passed]]、[[face_scan]]、[[certification_id]]、[[ca_certification_info]]。