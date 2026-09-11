---
type: enum
title: certification_type
page_key: certification_type
domain: 基线
status: draft
aliases: [法人三要素认证]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# certification_type

（权威枚举页：12 值，绑定方式 setter-evidence，主承载 cust_certification_info.certification_type；db 实测分布。）

```ground:enum
enum: certification_type
fields: [cust_certification_info.certification_type]
values:
  COMPANY_FOUR_ELEMENTS:
    label: 企业工商（四要素）认证
  COMPANY_TWO_ELEMENTS:
    label: 企业工商（二要素）认证
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
  LEGAL_THREE_ELEMENTS:
    label: 法人三要素认证
```

## 表述差异

- COMPANY_TWO_ELEMENTS: 权威「企业工商（二要素）认证」；另有表述 ['法人三要素认证']
