---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-change@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: cust_change_cfg
page_key: cust_change_cfg
domain: 企业建档
aliases:
- cust_change_cfg
anchors:
- cust_change_cfg
---
# cust_change_cfg

cust_change_cfg

```ground:table
table: cust_change_cfg
description: cust_change_cfg
inactive: false
fields:
- name: client_type
- name: code
- name: cust_type
- name: enable
- name: id
- name: item_code
```

```ground:relation
type: EQUI_JOIN
left: cust_change_record.alter_type_id
right: cust_change_cfg.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-change-cfg-schema
```
