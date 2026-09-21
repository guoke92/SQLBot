---
type: dict
title: cust_person_info.source
page_key: cust_person_info__source
belong: dicts
status: draft
anchors: [cust_person_info.source]
sources: ['database_profile:cust_person_info.source', 'database_schema:cust_person_info.source',
  'code_path:CustPersonInfoSourceEnum.java:17', 'code_path:CustPersonInfoSourceEnum.java:15']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.source

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_person_info.source`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__source
fields: [cust_person_info.source]
values:
  longteng: {trust: confirmed, label: 龙腾, evidence: 'code_path:CustPersonInfoSourceEnum.java:17'}
  AMS: {trust: confirmed, label: 管理员, evidence: 'code_path:CustPersonInfoSourceEnum.java:15'}
  jingke: {trust: proposed}
triage: hold
needs_review: true
```
