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
title: 租户开通的产品实例（每租户每产品至多一条；属性从 platform_product 拷贝）。
page_key: tenant_product
domain: 产品与配置
aliases:
- tenant_product
anchors:
- tenant_product
---
# tenant_product

租户开通的产品实例（每租户每产品至多一条；属性从 platform_product 拷贝）。

```ground:table
table: tenant_product
description: 租户开通的产品实例（每租户每产品至多一条；属性从 platform_product 拷贝）。
inactive: false
fields:
- name: name
- name: open_status
  dictionary: tenant-product-open
- name: platform_product_code
- name: platform_product_id
- name: ref_tenant_product_project_code
- name: ref_tenant_product_tenant_setting_config
- name: tenant_id
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.platform_product_id
right: platform_product.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-pcf-tp-create
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.ref_tenant_product_tenant_setting_config
right: tenant_setting_config.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-pcf-tp-create
```
