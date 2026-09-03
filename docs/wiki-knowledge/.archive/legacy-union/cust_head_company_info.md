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
title: cust_head_company_info
page_key: cust_head_company_info
domain: 企业建档
aliases:
- cust_head_company_info
anchors:
- cust_head_company_info
---
# cust_head_company_info

cust_head_company_info

```ground:table
table: cust_head_company_info
description: cust_head_company_info
inactive: false
fields:
- name: certification_no
- name: code
- name: enable
- name: id
- name: name
- name: ref_cust_head_company_info_cust_company_info
```

```ground:relation
type: EQUI_JOIN
left: cust_head_company_info.ref_cust_head_company_info_cust_company_info
right: cust_company_info.code
cardinality: n_to_1
status: proposed
evidence: code_path:ev-group-schema
```
