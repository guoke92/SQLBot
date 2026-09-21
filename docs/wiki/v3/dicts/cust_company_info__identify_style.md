---
type: dict
title: cust_company_info.identify_style
page_key: cust_company_info__identify_style
belong: dicts
status: draft
anchors: [cust_company_info.identify_style]
sources: ['database_profile:cust_company_info.identify_style', 'database_schema:cust_company_info.identify_style',
  'code_path:IdentifyTypeConstant.java:16', 'code_path:IdentifyTypeConstant.java:12',
  'code_path:IdentifyTypeConstant.java:20', 'code_path:IdentifyTypeConstant.java:24']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.identify_style

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_company_info.identify_style`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__identify_style
fields: [cust_company_info.identify_style]
values:
  INVITE_AGW: {trust: confirmed, label: 邀请认证-内管录入, evidence: 'code_path:IdentifyTypeConstant.java:16'}
  INVITE: {trust: confirmed, label: 邀请认证-客户录入, evidence: 'code_path:IdentifyTypeConstant.java:12'}
  SIMPLE: {trust: confirmed, label: 简易认证, evidence: 'code_path:IdentifyTypeConstant.java:20'}
  SELF: {trust: confirmed, label: 自主认证, evidence: 'code_path:IdentifyTypeConstant.java:24'}
triage: hold
needs_review: true
```
