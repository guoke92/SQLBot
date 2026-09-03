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
title: platform_product_client
page_key: platform_product_client
domain: product
aliases:
- platform_product_client
anchors:
- platform_product_client
---
# platform_product_client

platform_product_client

```ground:table
table: platform_product_client
description: platform_product_client
inactive: false
fields:
- name: client_type
- name: code
- name: enable
- name: id
- name: platform_product_id
- name: status
```

```ground:relation
type: EQUI_JOIN
left: platform_product_client.platform_product_id
right: platform_product.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-auth-agreement-schema
```
