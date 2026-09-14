---
type: caliber
title: 人工认证通过
page_key: manual_verify_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人工核查通过
  - manual passed
  - saveManual
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
contract_version: "0.1"
belong: calibers
---

# 人工认证通过

## 业务定位

只认 `manual_verify_status` 的人工通过态，用于人工核查落库与实名流程的短路返回：一旦人工通过，`verifyThree` 直接返回通过结论，不再走后续核查。

## 需求背景

自动核查可能失败，需人工兜底；人工通过后若继续走自动核查会产生无意义的调用与计数增长（见 [[tables/cust_certification_info|认证记录表]] 的 `auto_verify_count`）。

## 版本演进

从证据可见，人工通过与自动通过是并列两列，二者并集构成 [[calibers/face_verify_passed|人脸认证通过]]；状态含义见 [[processes/certification_verify_status|人脸/实名认证结果状态]]。

```ground:caliber
name: 人工认证通过
predicate: "cust_certification_info.manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'"
scope: 人工核查与实名短路返回
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveManual
```

关联页面：[[tables/cust_certification_info|认证记录表]]、[[concepts/face_auth_passed|人脸认证通过（术语）]]。