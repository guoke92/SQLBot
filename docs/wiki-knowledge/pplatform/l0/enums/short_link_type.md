---
type: enum
title: short_link_type
page_key: short_link_type
belong: enums
status: draft
aliases: []
anchors:
- short_link_type
sources:
- database_profile:short_link.type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# short_link_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: short_link_type
fields:
- short_link.type
values:
  NORMAL:
    confidence: proposed
  FILE:
    confidence: proposed
ambiguous: false
```
