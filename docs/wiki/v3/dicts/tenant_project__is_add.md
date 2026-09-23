---
type: dict
title: tenant_project.is_add
page_key: tenant_project__is_add
belong: dicts
status: draft
anchors:
- tenant_project.is_add
sources:
- database_profile:tenant_project.is_add
- database_schema:tenant_project.is_add
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- tenant_project
---
# tenant_project.is_add

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `tenant_project.is_add`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__is_add
fields:
- tenant_project.is_add
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
