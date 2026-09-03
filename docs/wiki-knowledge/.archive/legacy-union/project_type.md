---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-online-approval@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 项目类型
page_key: project_type
domain: 项目审批
aliases:
- 标准项目
- 常规项目
anchors:
- project_type
---
# 项目类型

STANDARD 标准项目 / REGULAR 常规项目（REGULAR 且低风险决定是否推 AMS）。

```ground:enum
enum: project_type
fields:
- tenant_project_approval.project_type
values:
  STANDARD:
    label: 标准项目
  REGULAR:
    label: 常规项目
```

## 关联
- [[tenant_project_approval|tenant_project_approval]]
