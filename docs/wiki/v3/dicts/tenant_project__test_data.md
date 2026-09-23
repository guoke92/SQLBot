---
type: dict
title: tenant_project.test_data
page_key: tenant_project__test_data
belong: dicts
status: draft
anchors:
- tenant_project.test_data
sources:
- database_profile:tenant_project.test_data
- agent:hold_promote
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related:
- tenant_project
---
# tenant_project.test_data

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 复审 promote：二元/开关码 + LLM 中文 label。
物理列 `tenant_project.test_data`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__test_data
fields:
- tenant_project.test_data
values:
  N:
    trust: proposed
    label: 否
  Y:
    trust: proposed
    label: 是
triage: keep
```
