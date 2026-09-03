---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:company-product-auth@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: cust_customized_product
page_key: cust_customized_product
domain: product
aliases:
- cust_customized_product
anchors:
- cust_customized_product
---
# cust_customized_product

cust_customized_product

```ground:table
table: cust_customized_product
description: cust_customized_product
inactive: false
fields:
- name: code
- name: cust_id
- name: enable
- name: id
- name: ref_cust_customized_product_cust_company_info
```

```ground:relation
type: EQUI_JOIN
left: cust_customized_product.cust_id
right: cust_company_info.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-auth-agreement-schema
```
