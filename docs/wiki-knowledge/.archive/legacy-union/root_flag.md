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
title: 集团根企业
page_key: root_flag
domain: 企业建档
aliases:
- 集团公司
- 根企业
anchors:
- root_flag
---
# 集团根企业

集团树根节点；root_flag=Y 表示集团企业，root_cust_id 指向该集团根企业。

```ground:enum
enum: root_flag
fields:
- cust_group_rel.root_flag
- cust_group_rel.root_cust_id
values:
  Y:
    label: 集团根企业
  N:
    label: 非根企业
```

## 关联
- [[cust_group_rel|cust_group_rel]]
