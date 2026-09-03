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
title: platform_product_cust_role
page_key: platform_product_cust_role
domain: product
aliases:
- platform_product_cust_role
anchors:
- platform_product_cust_role
---
# platform_product_cust_role

platform_product_cust_role

```ground:table
table: platform_product_cust_role
description: platform_product_cust_role
inactive: false
fields:
- name: code
- name: company_type_code
- name: enable
- name: id
- name: product_code
```

```ground:relation
type: EQUI_JOIN
left: platform_product_cust_role.product_code
right: platform_product.product_code
cardinality: n_to_1
status: proposed
evidence: code_path:ev-auth-agreement-schema
```
