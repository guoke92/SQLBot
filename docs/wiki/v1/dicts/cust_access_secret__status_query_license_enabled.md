---
type: dict
title: cust_access_secret.status_query_license_enabled
page_key: cust_access_secret__status_query_license_enabled
belong: dicts
status: draft
anchors: [cust_access_secret.status_query_license_enabled]
sources: ['database_profile:cust_access_secret.status_query_license_enabled', 'database_schema:cust_access_secret.status_query_license_enabled']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_access_secret]
---

# cust_access_secret.status_query_license_enabled

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_access_secret.status_query_license_enabled`，表页 [[tables/cust_access_secret]]。

## 取值

```ground:dict
dict: cust_access_secret__status_query_license_enabled
fields: [cust_access_secret.status_query_license_enabled]
values:
  N: {trust: proposed, label: 否, evidence: 'database_schema:cust_access_secret.status_query_license_enabled'}
  Y: {trust: proposed, label: 是, evidence: 'database_schema:cust_access_secret.status_query_license_enabled'}
triage: keep
```
