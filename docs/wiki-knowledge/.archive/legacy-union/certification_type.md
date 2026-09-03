---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 认证类型
page_key: certification_type
domain: 企业建档
aliases:
- 四要素
- 二要素
- 法人认证
- 人脸识别
- OCR
anchors:
- certification_type
---
# 认证类型

certification_type 使用 CustCertificationTypeEnum 的物理键区分企业、法人、客户管理员及证件核查认证方式。

```ground:enum
enum: certification_type
fields:
- cust_certification_info.certification_type
values:
  COMPANY_FOUR_ELEMENTS:
    label: 企业工商（四要素）认证
  COMPANY_TWO_ELEMENTS:
    label: 企业工商（二要素）认证
  LEGAL_THREE_ELEMENTS:
    label: 法人三要素认证
  LEGAL_REAL_NAME:
    label: 法人实名认证
  FACE_VERIFY:
    label: 人脸识别认证
  AUTH_THREE_ELEMENTS:
    label: 客户管理员三要素认证
  AUTH_REAL_NAME:
    label: 客户管理员实名认证
  LEGAL_OCR:
    label: 法人身份证OCR比对
  AUTH_OCR:
    label: 客户管理员身份证OCR比对
  LICENSE_OCR:
    label: 营业执照OCR比对
  LEGAL_MEDIA_OCR:
    label: 法人证件核查比对
  AUTH_MEDIA_OCR:
    label: 客户管理员证件核查比对
```

## 关联
- [[cust_certification_info|cust_certification_info]]
