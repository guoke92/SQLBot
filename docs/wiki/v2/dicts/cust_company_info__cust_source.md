---
type: dict
title: cust_company_info.cust_source
page_key: cust_company_info__cust_source
belong: dicts
status: draft
anchors: [cust_company_info.cust_source]
sources: ['database_profile:cust_company_info.cust_source']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cust_source

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_company_info.cust_source`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cust_source
fields: [cust_company_info.cust_source]
values:
  PPLATFORM: {trust: proposed}
  MIGRATORY: {trust: proposed}
  PLATFORM_PUSH: {trust: proposed}
  PLATFORM: {trust: proposed}
triage: hold
needs_review: true
```
