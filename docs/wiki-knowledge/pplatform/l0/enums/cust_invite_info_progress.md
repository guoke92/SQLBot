---
type: enum
title: cust_invite_info_progress
page_key: cust_invite_info_progress
belong: enums
status: draft
aliases: []
anchors:
- cust_invite_info_progress
sources:
- database_profile:cust_invite_info.progress
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# cust_invite_info_progress

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: cust_invite_info_progress
fields:
- cust_invite_info.progress
values:
  INIT:
    confidence: proposed
  CUST_CONFIRM_AWAIT:
    confidence: proposed
  BUILD_SUCCESS:
    confidence: proposed
  CUST_BUILDING:
    confidence: proposed
  CUST_CHANGE:
    confidence: proposed
  BUILD_FAIL:
    confidence: proposed
  AWAIT_CUST_CONFIRM:
    confidence: proposed
ambiguous: false
```
