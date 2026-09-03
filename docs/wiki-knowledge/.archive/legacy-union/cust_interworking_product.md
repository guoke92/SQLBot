---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:interworking-products@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 企业互通产品开通表（"开通"=跨系统统一授权通过）。
page_key: cust_interworking_product
domain: 产品与配置
aliases:
- cust_interworking_product
anchors:
- cust_interworking_product
---
# cust_interworking_product

企业互通产品开通表（"开通"=跨系统统一授权通过）。

```ground:table
table: cust_interworking_product
description: 企业互通产品开通表（"开通"=跨系统统一授权通过）。
inactive: false
fields:
- name: cust_id
- name: open_status
  dictionary: interworking-open-status
- name: open_time
- name: product_id
```

```ground:relation
type: EQUI_JOIN
left: cust_interworking_product.product_id
right: tenant_interworking_product.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-iwp-cust-open
```
