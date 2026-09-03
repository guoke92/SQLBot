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
type: table
title: cust_group_rel
page_key: cust_group_rel
domain: 企业建档
aliases:
- cust_group_rel
anchors:
- cust_group_rel
---
# cust_group_rel

cust_group_rel

```ground:table
table: cust_group_rel
description: cust_group_rel
inactive: false
fields:
- name: cust_id
- name: enable
- name: id
- name: parent_cust_id
- name: root_cust_id
- name: root_flag
- name: status
```

```ground:relation
type: EQUI_JOIN
left: cust_group_rel.cust_id
right: cust_company_info.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-group-schema
```
