---
type: dict
title: cust_certification_info.certification_type
page_key: cust_certification_info__certification_type
belong: dicts
status: draft
anchors: [cust_certification_info.certification_type]
sources: ['database_profile:cust_certification_info.certification_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_certification_info]
---

# cust_certification_info.certification_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_certification_info.certification_type`，表页 [[tables/cust_certification_info]]。

## 取值

```ground:dict
dict: cust_certification_info__certification_type
fields: [cust_certification_info.certification_type]
values:
  FACE_VERIFY: {trust: proposed}
  AUTH_THREE_ELEMENTS: {trust: proposed}
  LEGAL_REAL_NAME: {trust: proposed}
  LEGAL_THREE_ELEMENTS: {trust: proposed}
  COMPANY_TWO_ELEMENTS: {trust: proposed}
  LEGAL_OCR: {trust: proposed}
  AUTH_MEDIA_OCR: {trust: proposed}
triage: keep
```
