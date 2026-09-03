---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:product-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 全局产品目录（一行一类产品；product_ref_num 为被开通租户数冗余计数）。
page_key: platform_product
domain: 产品与配置
aliases:
- platform_product
anchors:
- platform_product
---
# platform_product

全局产品目录（一行一类产品；product_ref_num 为被开通租户数冗余计数）。

```ground:table
table: platform_product
description: 全局产品目录（一行一类产品；product_ref_num 为被开通租户数冗余计数）。
inactive: false
fields:
- name: product_ref_num
- name: product_status
  dictionary: platform-product-status
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.platform_product_id
right: platform_product.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-pcf-tp-create
```
