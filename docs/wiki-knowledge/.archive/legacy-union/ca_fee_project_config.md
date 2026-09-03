---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: CA 服务费项目收费配置（按项目一行，参与租户过滤）：开关、角色年费、拦截场景、 特殊企业清单。每项目一配置（uk project_id）。
page_key: ca_fee_project_config
domain: CA认证与服务费
aliases:
- ca_fee_project_config
anchors:
- ca_fee_project_config
---
# ca_fee_project_config

CA 服务费项目收费配置（按项目一行，参与租户过滤）：开关、角色年费、拦截场景、 特殊企业清单。每项目一配置（uk project_id）。

```ground:table
table: ca_fee_project_config
description: CA 服务费项目收费配置（按项目一行，参与租户过滤）：开关、角色年费、拦截场景、 特殊企业清单。每项目一配置（uk project_id）。
inactive: false
fields:
- name: special_company_list
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_order.project_id
right: ca_fee_project_config.project_id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-cfc-order-close
```
