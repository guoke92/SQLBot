---
type: dict
title: cust_certification_info.certification_type
page_key: cust_certification_info__certification_type
belong: dicts
status: draft
anchors: [cust_certification_info.certification_type]
sources: ['database_profile:cust_certification_info.certification_type', 'database_schema:cust_certification_info.certification_type',
  'code_path:CustCertificationTypeEnum.java:17', 'code_path:CustCertificationTypeEnum.java:18',
  'code_path:CustCertificationTypeEnum.java:16', 'code_path:CustCertificationTypeEnum.java:15',
  'code_path:CustCertificationTypeEnum.java:14', 'code_path:CustCertificationTypeEnum.java:20',
  'code_path:CustCertificationTypeEnum.java:24']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_certification_info]
---

# cust_certification_info.certification_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_certification_info.certification_type`，表页 [[tables/cust_certification_info]]。

## 取值

```ground:dict
dict: cust_certification_info__certification_type
fields: [cust_certification_info.certification_type]
values:
  FACE_VERIFY: {trust: confirmed, label: 人脸识别认证, evidence: 'code_path:CustCertificationTypeEnum.java:17'}
  AUTH_THREE_ELEMENTS: {trust: confirmed, label: 客户管理员三要素认证, evidence: 'code_path:CustCertificationTypeEnum.java:18'}
  LEGAL_REAL_NAME: {trust: confirmed, label: 法人实名认证, evidence: 'code_path:CustCertificationTypeEnum.java:16'}
  LEGAL_THREE_ELEMENTS: {trust: confirmed, label: 法人三要素认证, evidence: 'code_path:CustCertificationTypeEnum.java:15'}
  COMPANY_TWO_ELEMENTS: {trust: confirmed, label: 企业工商（二要素）认证, evidence: 'code_path:CustCertificationTypeEnum.java:14'}
  LEGAL_OCR: {trust: confirmed, label: 法人身份证OCR比对, evidence: 'code_path:CustCertificationTypeEnum.java:20'}
  AUTH_MEDIA_OCR: {trust: confirmed, label: 客户管理员证件核查比对, evidence: 'code_path:CustCertificationTypeEnum.java:24'}
triage: keep
```
