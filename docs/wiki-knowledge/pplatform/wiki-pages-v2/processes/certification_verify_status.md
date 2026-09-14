---
type: process
title: 人脸/实名认证结果状态机
page_key: certification_verify_status
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 人脸认证结果状态
  - 实名认证结果状态
  - auto_verify_status 状态机
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
belong: processes
---

# 人脸/实名认证结果状态机

## 业务定位

描述 [[tables/cust_certification_info|认证记录表]] 中 `auto_verify_status` 与 `manual_verify_status` 的取值与流转：自动核查通过/失败、人工核查通过三态。该状态机是 [[calibers/face_verify_passed|人脸认证通过]] 与 [[calibers/manual_verify_passed|人工认证通过]] 两个口径的直接来源，通过后由 [[processes/ca_submit_status|CFCA 上送状态]] 链路把结果用于意愿数据回填。

## 需求背景

自动核查失败不是终态：再次自动核查通过可回写为自动通过；也可由人工核查兜底为人工通过。`verifyThree` 在人工认证已通过时短路返回，避免重复核查。人脸查询侧 `isFaceVerifyPassed` 只要自动或人工任一通过即视为人脸通过，从而触发 `intent_h5_face_json` 回填。

## 版本演进

从代码可见：状态值使用枚举名（code_enum）形式写入；随后出现「人工通过短路」的优化分支；需注意写入用 `getDictParam()`、判断用 `getDictKey()` 的读写键不一致风险，见 [[rules/verify_status_dict_key_consistency|核查状态字典键一致性规则]]。

```ground:process
name: 人脸/实名认证结果状态
field: cust_certification_info.auto_verify_status / cust_certification_info.manual_verify_status
states:
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动认证通过
    source: code_enum
  - value: AUTOMATIC_AUTHENTICATION_FAILED
    label: 自动认证失败
    source: code_enum
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工认证通过
    source: code_enum
transitions:
  - from: AUTOMATIC_AUTHENTICATION_FAILED
    event: 自动核查再次通过
    to: AUTOMATIC_AUTHENTICATION_PASSED
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveOrUpdate
  - from: AUTOMATIC_AUTHENTICATION_FAILED
    event: 人工核查通过
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveManual
  - from: 未通过
    event: 人脸查询结果自动或人工任一通过
    to: 人脸认证通过
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java:isFaceVerifyPassed
  - from: 未通过
    event: 人工认证已通过时短路返回
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:verifyThree
```

关联页面：[[concepts/face_auth_passed|人脸认证通过（术语）]]、[[calibers/manual_verify_passed|人工认证通过]]。

---REVIEW: process | 人脸/实名认证结果状态机---
第 3、4 条流转的 from/to 使用业务标签「未通过 / 人脸认证通过」「MANUAL_AUTHENTICATION_PASSED」，语义分析未给出对应的枚举 value（如人脸通过的统一 value），因此按标签原样保留，待枚举口径补充后再对齐 value。
---END REVIEW---