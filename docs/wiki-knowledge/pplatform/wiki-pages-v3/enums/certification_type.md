---
type: enum
title: certification_type
page_key: certification_type
domain: 基线
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustCertificationTypeConstant"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# certification_type

[[cust_person_info]] 的 `certification_type`。

```ground:enum
enum: certification_type
fields: [cust_person_info.certification_type]
values:
  "AUTH_MEDIA_OCR":
    label: "客户管理员证件核查比对"
  "AUTH_OCR":
    label: "客户管理员身份证OCR比对"
  "AUTH_REAL_NAME":
    label: "客户管理员实名认证"
  "AUTH_THREE_ELEMENTS":
    label: "客户管理员三要素认证"
  "BUSI_LICENCE_NO":
    label: "营业执照号码"
  "CERT_GREEN_CARD":
    label: "外国人永久居留证"
  "CERT_HK_AND_MACAU_PASS":
    label: "港澳通行证"
  "CERT_MAINLAND_PASS":
    label: "港澳居民来往内地通行证"
  "CERT_OTHER":
    label: "其他"
  "CERT_PASSPORT":
    label: "护照"
  "CERT_RESIDENT_PERMIT":
    label: "港澳台居民居住证"
  "CERT_TAIWAN":
    label: "台胞证"
  "CERT_TAIWAN_PASS":
    label: "台湾通行证"
  "COMPANY_FOUR_ELEMENTS":
    label: "企业工商（四要素）认证"
  "COMPANY_TWO_ELEMENTS":
    label: "企业工商（二要素）认证"
  "CRET_ID":
    label: "二代居民身份证"
  "CRET_ID_HK":
    label: "香港身份证"
  "FACE_VERIFY":
    label: "人脸识别认证"
  "LEGAL_CERTIFICATE":
    label: "事业单位法人证书"
  "LEGAL_MEDIA_OCR":
    label: "法人证件核查比对"
  "LEGAL_OCR":
    label: "法人身份证OCR比对"
  "LEGAL_REAL_NAME":
    label: "法人实名认证"
  "LEGAL_THREE_ELEMENTS":
    label: "法人三要素认证"
  "LICENSE_OCR":
    label: "营业执照OCR比对"
  "SOCIAL_ORG_CERTIFICATE":
    label: "社会团体登记证书"
  "SOCIAL_UNIFIED_CODE":
    label: "企业统一社会信用代码"
```
