---
type: dict
title: cust_person_info.certification_type
page_key: cust_person_info__certification_type
belong: dicts
status: draft
anchors: [cust_person_info.certification_type]
sources: ['database_profile:cust_person_info.certification_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.certification_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_person_info.certification_type`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__certification_type
fields: [cust_person_info.certification_type]
values:
  CRET_ID: {trust: proposed}
  CREDENTIALS_ID: {trust: proposed}
  CERT_RESIDENT_PERMIT: {trust: proposed}
  CERT_PASSPORT: {trust: proposed}
  CERT_GREEN_CARD: {trust: proposed}
  CERT_TAIWAN: {trust: proposed}
  CERT_MAINLAND_PASS: {trust: proposed}
  CERT_HK_AND_MACAU_PASS: {trust: proposed}
  CRET_ID_HK: {trust: proposed}
triage: keep
```
