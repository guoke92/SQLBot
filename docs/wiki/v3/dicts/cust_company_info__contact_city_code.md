---
type: dict
title: cust_company_info.contact_city_code
page_key: cust_company_info__contact_city_code
belong: dicts
status: draft
anchors: [cust_company_info.contact_city_code]
sources: ['database_profile:cust_company_info.contact_city_code']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.contact_city_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_company_info.contact_city_code`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__contact_city_code
fields: [cust_company_info.contact_city_code]
values:
  '820000': {trust: proposed}
  '650200': {trust: proposed}
triage: hold
needs_review: true
```
