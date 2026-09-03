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
title: 建档推送运营中台记录（含中台返回的企业/人员 id，回调匹配锚点）。
page_key: cust_build_record
domain: 客户与建档
aliases:
- cust_build_record
anchors:
- cust_build_record
---
# cust_build_record

建档推送运营中台记录（含中台返回的企业/人员 id，回调匹配锚点）。

```ground:table
table: cust_build_record
description: 建档推送运营中台记录（含中台返回的企业/人员 id，回调匹配锚点）。
inactive: false
fields:
- name: channel
- name: cust_id
- name: person_id
- name: plat_cust_id
- name: plat_person_id
- name: return_data
```

```ground:relation
type: EQUI_JOIN
left: cust_build_record.cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-push-record
```

```ground:relation
type: EQUI_JOIN
left: cust_build_record.person_id
right: cust_person_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-push-record
```
