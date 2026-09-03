---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:tenant-project-lifecycle@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 项目状态
page_key: project_status
domain: 项目管理
aliases:
- 待生效
- 已生效
- 已失效
anchors:
- project_status
---
# 项目状态

tenant_project.project_status 使用 0/1/2 表示项目生命周期状态。

```ground:enum
enum: project_status
fields:
- tenant_project.project_status
values:
  '0':
    label: 待生效
  '1':
    label: 已生效
  '2':
    label: 已失效
```

## 关联
- [[tenant_project|tenant_project]]
