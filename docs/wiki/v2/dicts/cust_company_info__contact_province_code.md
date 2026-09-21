---
type: dict
title: cust_company_info.contact_province_code
page_key: cust_company_info__contact_province_code
belong: dicts
status: draft
anchors: [cust_company_info.contact_province_code]
sources: ['database_profile:cust_company_info.contact_province_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.contact_province_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_company_info.contact_province_code`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__contact_province_code
fields: [cust_company_info.contact_province_code]
values:
  '820000': {trust: proposed}
  '650000': {trust: proposed}
triage: hold
needs_review: true
```
