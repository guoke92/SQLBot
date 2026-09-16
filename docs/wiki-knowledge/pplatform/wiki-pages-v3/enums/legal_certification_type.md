---
type: enum
title: legal_certification_type
page_key: legal_certification_type
domain: 基线
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:IDTypeEnum.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# legal_certification_type

[[cust_company_info]] 的 `legal_certification_type`。

```ground:enum
enum: legal_certification_type
fields: [cust_company_info.legal_certification_type]
values:
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
  "CRET_ID":
    label: "二代居民身份证"
  "CRET_ID_HK":
    label: "香港身份证"
  "LEGAL_CERTIFICATE":
    label: "事业单位法人证书"
  "SOCIAL_ORG_CERTIFICATE":
    label: "社会团体登记证书"
  "SOCIAL_UNIFIED_CODE":
    label: "企业统一社会信用代码"
```
