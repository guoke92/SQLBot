---
type: enum
title: cust_auth_application_open_status
page_key: cust_auth_application_open_status
belong: enums
status: draft
aliases: []
anchors:
- cust_auth_application_open_status
sources:
- database_profile:cust_auth_application.open_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_auth_application_open_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_auth_application_open_status
fields:
- cust_auth_application.open_status
values:
  OPENING:
    confidence: proposed
  OPENED:
    confidence: proposed
  NOT_OPENED:
    confidence: proposed
ambiguous: false
```
