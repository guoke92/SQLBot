---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:customer-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: cust_setting_config
page_key: cust_setting_config
domain: 企业建档
aliases:
- cust_setting_config
anchors:
- cust_setting_config
---
# cust_setting_config

cust_setting_config

```ground:table
table: cust_setting_config
description: cust_setting_config
inactive: false
fields:
- name: code
- name: cust_id
- name: enable
- name: id
- name: name
```

```ground:relation
type: EQUI_JOIN
left: cust_setting_config.cust_id
right: cust_company_info.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-config-mapping-schema
```
