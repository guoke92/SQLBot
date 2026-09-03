---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:user-account@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: cust_user_rel
page_key: cust_user_rel
domain: user
aliases:
- cust_user_rel
anchors:
- cust_user_rel
---
# cust_user_rel

cust_user_rel

```ground:table
table: cust_user_rel
description: cust_user_rel
inactive: false
fields:
- name: code
- name: company_id
- name: company_type
- name: enable
- name: id
- name: user_id
- name: user_type
```

```ground:relation
type: EQUI_JOIN
left: cust_user_rel.company_id
right: cust_company_info.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-user-rel-schema
```
