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
title: 企业主数据/过程记录，一行一家企业（data_type 区分主数据/流程行/暂存行）。
page_key: cust_company_info
domain: 客户与建档
aliases:
- cust_company_info
anchors:
- cust_company_info
---
# cust_company_info

企业主数据/过程记录，一行一家企业（data_type 区分主数据/流程行/暂存行）。

```ground:table
table: cust_company_info
description: 企业主数据/过程记录，一行一家企业（data_type 区分主数据/流程行/暂存行）。
inactive: false
fields:
- name: cust_status
  dictionary: freeze-status
```

```ground:relation
type: EQUI_JOIN
left: cust_company_lifecycle_info.company_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-eso-freeze
```
