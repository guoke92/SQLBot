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
title: 租户运营配置（含 default_project_id 建档默认项目、project_code_required 项目码必填联动）。
page_key: tenant_setting_config
domain: 产品与配置
aliases:
- tenant_setting_config
anchors:
- tenant_setting_config
---
# tenant_setting_config

租户运营配置（含 default_project_id 建档默认项目、project_code_required 项目码必填联动）。

```ground:table
table: tenant_setting_config
description: 租户运营配置（含 default_project_id 建档默认项目、project_code_required 项目码必填联动）。
inactive: false
fields:
- name: default_project_id
- name: project_code_required
```

```ground:relation
type: EQUI_JOIN
left: tenant_product.ref_tenant_product_tenant_setting_config
right: tenant_setting_config.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-pcf-tp-create
```
