---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-auxiliary@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: cust_shareholder_info
page_key: cust_shareholder_info
domain: 企业建档
aliases:
- cust_shareholder_info
anchors:
- cust_shareholder_info
---
# cust_shareholder_info

cust_shareholder_info

```ground:table
table: cust_shareholder_info
description: cust_shareholder_info
inactive: false
fields:
- name: certification_no
- name: certification_type
- name: code
- name: enable
- name: fund_type
- name: id
- name: ref_cust_company_info
- name: relation_type
```

```ground:relation
type: EQUI_JOIN
left: cust_shareholder_info.ref_cust_company_info
right: cust_company_info.code
cardinality: n_to_1
status: proposed
evidence: code_path:ev-shareholder-schema
```
