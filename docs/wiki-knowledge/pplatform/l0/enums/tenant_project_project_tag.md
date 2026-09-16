---
type: enum
title: tenant_project_project_tag
page_key: tenant_project_project_tag
belong: enums
status: draft
aliases: []
anchors:
- tenant_project_project_tag
sources:
- database_profile:tenant_project.project_tag
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_project_project_tag

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_project_project_tag
fields:
- tenant_project.project_tag
values:
  PRD:
    confidence: proposed
  TEST:
    confidence: proposed
ambiguous: false
```
