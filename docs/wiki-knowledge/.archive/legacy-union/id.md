---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:company-group@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 集团成员
page_key: id
domain: 企业建档
aliases:
- 成员单位
- 集团关系
anchors:
- id
---
# 集团成员

cust_group_rel 中一行企业节点，记录成员、父级、根集团、企业角色和关系状态。

```ground:enum
enum: id
fields:
- cust_group_rel.id
- cust_group_rel.cust_id
- cust_group_rel.status
values:
  EFFECTIVE:
    label: 已生效
  INEFFECTIVE:
    label: 未生效
  REJECTED:
    label: 已拒绝
```

## 关联
- [[cust_group_rel|cust_group_rel]]
