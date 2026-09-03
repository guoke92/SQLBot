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
type: rule
title: 开通状态不是 OPENED
page_key: 开通状态不是-OPENED
domain: 项目管理
field_targets:
- cust_project_rel.project_open_status
---
# 开通状态不是 OPENED

项目开通状态字段是 project_open_status，值为 Y/P/N。

```ground:rule
rule: open-status-is-ynp
field_targets:
- cust_project_rel.project_open_status
impact: query_constraint
content: 项目开通状态字段是 project_open_status，值为 Y/P/N。
scope: 已开通项目、开通中项目
```

## 关联
- [[cust_project_rel]]
