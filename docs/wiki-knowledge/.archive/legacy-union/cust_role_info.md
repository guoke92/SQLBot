---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-build-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 企业角色记录（企业建档时随建，status=ADD）。
page_key: cust_role_info
domain: 客户与建档
aliases:
- cust_role_info
anchors:
- cust_role_info
---
# cust_role_info

企业角色记录（企业建档时随建，status=ADD）。

```ground:table
table: cust_role_info
description: 企业角色记录（企业建档时随建，status=ADD）。
inactive: false
fields:
- name: code
- name: ref_cust_company_info
- name: status
```

```ground:relation
type: EQUI_JOIN
left: cust_role_info.ref_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-flow-company-code
```

```ground:relation
type: SHARED_KEY
left: cust_role_info.platform_cust_id
right: cust_company_info.platform_cust_id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-push-record
```
