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
title: 租户互通产品开通实例（全局共享不参与租户行过滤）。
page_key: tenant_interworking_product
domain: 产品与配置
aliases:
- tenant_interworking_product
anchors:
- tenant_interworking_product
---
# tenant_interworking_product

租户互通产品开通实例（全局共享不参与租户行过滤）。

```ground:table
table: tenant_interworking_product
description: 租户互通产品开通实例（全局共享不参与租户行过滤）。
inactive: false
fields:
- name: max_financing_amount
- name: open_status
  dictionary: tenant-interworking-open
- name: platform_product_code
- name: scope
  dictionary: scope
- name: scope_project
- name: scope_role
- name: tenant_id
```

```ground:relation
type: EQUI_JOIN
left: cust_interworking_product.product_id
right: tenant_interworking_product.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-iwp-cust-open
```
