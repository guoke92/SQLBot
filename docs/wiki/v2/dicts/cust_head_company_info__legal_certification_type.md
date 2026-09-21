---
type: dict
title: cust_head_company_info.legal_certification_type
page_key: cust_head_company_info__legal_certification_type
belong: dicts
status: draft
anchors: [cust_head_company_info.legal_certification_type]
sources: ['database_profile:cust_head_company_info.legal_certification_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_head_company_info]
---

# cust_head_company_info.legal_certification_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_head_company_info.legal_certification_type`，表页 [[tables/cust_head_company_info]]。

## 取值

```ground:dict
dict: cust_head_company_info__legal_certification_type
fields: [cust_head_company_info.legal_certification_type]
values:
  CRET_ID: {trust: proposed}
  CERT_MAINLAND_PASS: {trust: proposed}
  CERT_PASSPORT: {trust: proposed}
  身份证: {trust: proposed}
  CERT_GREEN_CARD: {trust: proposed}
  CERT_TAIWAN: {trust: proposed}
  CRET_ID_HK: {trust: proposed}
triage: keep
```
