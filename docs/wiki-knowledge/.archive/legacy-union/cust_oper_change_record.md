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
type: table
title: cust_oper_change_record
page_key: cust_oper_change_record
domain: operation
aliases:
- cust_oper_change_record
anchors:
- cust_oper_change_record
---
# cust_oper_change_record

cust_oper_change_record

```ground:table
table: cust_oper_change_record
description: cust_oper_change_record
inactive: false
fields:
- name: after_operator_id
- name: before_operator_id
- name: change_type
- name: company_id
- name: enable
- name: id
- name: person_id
```

```ground:relation
type: EQUI_JOIN
left: cust_oper_change_record.company_id
right: cust_company_info.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-operation-user-schema
```

```ground:relation
type: EQUI_JOIN
left: cust_oper_change_record.person_id
right: cust_person_info.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-operation-user-schema
```
