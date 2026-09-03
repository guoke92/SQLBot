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
title: 企业联系人/经办人（管理员 admin 或访客 guest）。
page_key: cust_person_info
domain: 客户与建档
aliases:
- cust_person_info
anchors:
- cust_person_info
---
# cust_person_info

企业联系人/经办人（管理员 admin 或访客 guest）。

```ground:table
table: cust_person_info
description: 企业联系人/经办人（管理员 admin 或访客 guest）。
inactive: false
fields:
- name: code
- name: company_type
- name: cust_build_status
- name: cust_company_id
- name: main_data_id
- name: ref_cust_company_info
- name: status
- name: user_type
```

```ground:relation
type: EQUI_JOIN
left: cust_person_info.ref_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-flow-company-code
```

```ground:relation
type: EQUI_JOIN
left: cust_person_info.cust_company_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-flow-company-code
```

```ground:relation
type: EQUI_JOIN
left: cust_build_record.person_id
right: cust_person_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-push-record
```
