---
type: caliber
title: 人脸认证通过
page_key: face_verify_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人脸通过判断
  - isFaceVerifyPassed
  - 扫脸通过
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
belong: calibers
---

# 人脸认证通过

## 业务定位

「人脸认证通过」是扫脸链路的准入口径：自动核查通过或人工核查通过任一成立即为通过。它决定 `faceVerifyQuery` 是否把 DBaaS 请求/响应原文回填到 [[tables/ca_certification_info|CFCA 认证与上送表]] 的 `intent_h5_face_json`（见 [[concepts/h5_face_intent|H5刷脸意愿]]）。

## 需求背景

人脸查询接口在返回结果前需判断认证是否通过，只有通过才允许落意愿认证块，避免未通过数据被上报签章中台（见 [[processes/ca_submit_status|CFCA 上送状态]]）。

## 版本演进

从代码可见，该口径以「自动 OR 人工」的并集形式实现，与 [[calibers/manual_verify_passed|人工认证通过]] 的单一条件形成上下位关系；状态值来源见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。

```ground:caliber
name: 人脸认证通过
predicate: "cust_certification_info.auto_verify_status = 'AUTOMATIC_AUTHENTICATION_PASSED' OR cust_certification_info.manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'"
scope: faceVerifyQuery 回填 CFCA H5_FACE 意愿数据前的人脸通过判断
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java:isFaceVerifyPassed
```

关联页面：[[tables/cust_certification_info|认证记录表]]、[[concepts/saolian|扫脸]]。