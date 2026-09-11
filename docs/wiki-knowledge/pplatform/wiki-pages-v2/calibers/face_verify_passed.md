---
type: caliber
title: 人脸核查通过
page_key: caliber/face_verify_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases: [人脸通过, 刷脸通过]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# 人脸核查通过

人脸核查是否通过的判定口径：自动核查通过或人工核查通过，任一满足即视为通过。该口径决定是否回填 [[ca_certification_info]] 的 `intent_h5_face_json`。

## 需求背景

自动核查可能失败，需人工复核兜底，因此「通过」采用自动 / 人工或关系而非与关系。

## 版本演进

v0.1 记录单条判定谓词。

```ground:caliber
name: 人脸核查通过
predicate: "cust_certification_info.auto_verify_status = 'AUTOMATIC_AUTHENTICATION_PASSED' OR cust_certification_info.manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'"
scope: "FaceVerifyController#persistH5FaceIntentIfPassed 决定是否回填 intent_h5_face_json；两者任一通过即视为通过。"
evidence: code_path:FaceVerifyController.java#isFaceVerifyPassed
```

相关：[[cust_certification_info]]、[[realname_face_verify_state]]、[[h5_face_persist_soft_fail]]、[[face_scan]]。