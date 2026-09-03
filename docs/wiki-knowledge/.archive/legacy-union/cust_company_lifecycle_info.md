---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-status-operations@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 企业冻结/解冻生命周期台账（预生成草稿 enable=N，确认后 Y）。
page_key: cust_company_lifecycle_info
domain: 客户与建档
aliases:
- cust_company_lifecycle_info
anchors:
- cust_company_lifecycle_info
---
# cust_company_lifecycle_info

企业冻结/解冻生命周期台账（预生成草稿 enable=N，确认后 Y）。

```ground:table
table: cust_company_lifecycle_info
description: 企业冻结/解冻生命周期台账（预生成草稿 enable=N，确认后 Y）。
inactive: false
fields:
- name: attach
- name: company_id
- name: enable
- name: reason
- name: type
  dictionary: lifecycle-type
```

```ground:relation
type: EQUI_JOIN
left: cust_company_lifecycle_info.company_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-eso-freeze
```
