---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:op-user-coverage@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 离职置顶
page_key: top_flag
domain: operation
aliases:
- topFlag
- 置顶项目
anchors:
- top_flag
---
# 离职置顶

项目或项目企业关系上的置顶标记；值为 '1' 时检查关联运营字段，确认项目及其企业均无离职人员后才清为 '0'。

```ground:enum
enum: top_flag
fields:
- wec_project_operation_rel.top_flag
- wec_project_cust_operation_rel.top_flag
values:
  '1':
    label: 置顶
  '0':
    label: 未置顶
```

## 关联
- [[wec_project_cust_operation_rel|wec_project_cust_operation_rel]]
- [[wec_project_operation_rel|wec_project_operation_rel]]
