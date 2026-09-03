---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-code@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: cust_project_code_record
page_key: cust_project_code_record
domain: 项目管理
aliases:
- cust_project_code_record
anchors:
- cust_project_code_record
---
# cust_project_code_record

cust_project_code_record

```ground:table
table: cust_project_code_record
description: cust_project_code_record
inactive: false
fields:
- name: channel_code
- name: code
- name: company_id
- name: company_type
- name: enable
- name: id
- name: status
- name: type
- name: use_id
```

```ground:relation
type: EQUI_JOIN
left: cust_project_code_record.company_id
right: cust_company_info.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-project-code-schema
```
