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
title: 企业-项目-产品关系（一个企业在一个项目下一种角色一行）。
page_key: cust_project_rel
domain: 客户与建档
aliases:
- cust_project_rel
anchors:
- cust_project_rel
---
# cust_project_rel

企业-项目-产品关系（一个企业在一个项目下一种角色一行）。

```ground:table
table: cust_project_rel
description: 企业-项目-产品关系（一个企业在一个项目下一种角色一行）。
inactive: false
fields:
- name: code
- name: company_type
- name: product_id
- name: project_id
- name: ref_cust_project_rel_cust_company_info
- name: show_flag
- name: status
```

```ground:relation
type: EQUI_JOIN
left: cust_project_rel.ref_cust_project_rel_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ebc-flow-company-code
```
