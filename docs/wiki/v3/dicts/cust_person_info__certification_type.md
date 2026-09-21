---
type: dict
title: cust_person_info.certification_type
page_key: cust_person_info__certification_type
belong: dicts
status: draft
anchors: [cust_person_info.certification_type]
sources: ['database_profile:cust_person_info.certification_type', 'database_schema:cust_person_info.certification_type',
  'code_path:IDTypeEnum.java:17', 'code_path:IDTypeEnum.java:26', 'code_path:IDTypeEnum.java:21',
  'code_path:IDTypeEnum.java:20', 'code_path:IDTypeEnum.java:19', 'code_path:IDTypeEnum.java:18',
  'code_path:IDTypeEnum.java:24', 'code_path:IDTypeEnum.java:23']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.certification_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_person_info.certification_type`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__certification_type
fields: [cust_person_info.certification_type]
values:
  CRET_ID: {trust: confirmed, label: 二代居民身份证, evidence: 'code_path:IDTypeEnum.java:17'}
  CREDENTIALS_ID: {trust: proposed}
  CERT_RESIDENT_PERMIT: {trust: confirmed, label: 港澳台居民居住证, evidence: 'code_path:IDTypeEnum.java:26'}
  CERT_PASSPORT: {trust: confirmed, label: 护照, evidence: 'code_path:IDTypeEnum.java:21'}
  CERT_GREEN_CARD: {trust: confirmed, label: 外国人永久居留证, evidence: 'code_path:IDTypeEnum.java:20'}
  CERT_TAIWAN: {trust: confirmed, label: 台胞证, evidence: 'code_path:IDTypeEnum.java:19'}
  CERT_MAINLAND_PASS: {trust: confirmed, label: 港澳居民来往内地通行证, evidence: 'code_path:IDTypeEnum.java:18'}
  CERT_HK_AND_MACAU_PASS: {trust: confirmed, label: 港澳通行证, evidence: 'code_path:IDTypeEnum.java:24'}
  CRET_ID_HK: {trust: confirmed, label: 香港身份证, evidence: 'code_path:IDTypeEnum.java:23'}
triage: keep
```
