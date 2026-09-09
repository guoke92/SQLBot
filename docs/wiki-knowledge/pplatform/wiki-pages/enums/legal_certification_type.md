---
type: enum
title: legal_certification_type
page_key: legal_certification_type
belong: enums
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# legal_certification_type

（权威枚举页：14 值，绑定方式 setter-evidence，主承载 cust_head_company_info.legal_certification_type；db 实测分布，基线外 1 值。）

```ground:enum
enum: legal_certification_type
fields: [cust_head_company_info.legal_certification_type, cust_person_info.certification_type, cust_company_info.legal_certification_type]
values:
  CRET_ID:
    label: 二代居民身份证
  CERT_MAINLAND_PASS:
    label: 港澳居民来往内地通行证
  CERT_TAIWAN:
    label: 台胞证
  CERT_GREEN_CARD:
    label: 外国人永久居留证
  CERT_PASSPORT:
    label: 护照
  BUSI_LICENCE_NO:
    label: 营业执照号码
  CRET_ID_HK:
    label: 香港身份证
  CERT_HK_AND_MACAU_PASS:
    label: 港澳通行证
  CERT_TAIWAN_PASS:
    label: 台湾通行证
  CERT_RESIDENT_PERMIT:
    label: 港澳台居民居住证
  SOCIAL_ORG_CERTIFICATE:
    label: 社会团体登记证书
  SOCIAL_UNIFIED_CODE:
    label: 企业统一社会信用代码
  LEGAL_CERTIFICATE:
    label: 事业单位法人证书
  CERT_OTHER:
    label: 其他
  身份证:
    label: "身份证"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
