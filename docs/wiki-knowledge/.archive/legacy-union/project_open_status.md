---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-enterprise-rel@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 项目开通
page_key: project_open_status
domain: project-enterprise
aliases:
- 已开通项目
- 项目开通状态
anchors:
- project_open_status
---
# 项目开通

关系表的 project_open_status 表示项目开通进度，值来自 ProductOpenStatusEnum：Y 已开通、P 开通中、N 未开通。

```ground:enum
enum: project_open_status
fields:
- cust_project_rel.project_open_status
values:
  Y:
    label: 已开通
  P:
    label: 开通中
  N:
    label: 未开通
```

## 关联
- [[cust_project_rel|cust_project_rel]]
