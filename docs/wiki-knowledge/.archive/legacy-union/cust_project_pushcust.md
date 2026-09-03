---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-code@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: cust_project_pushcust
page_key: cust_project_pushcust
domain: 项目管理
aliases:
- cust_project_pushcust
anchors:
- cust_project_pushcust
---
# cust_project_pushcust

cust_project_pushcust

```ground:table
table: cust_project_pushcust
description: cust_project_pushcust
inactive: false
fields:
- name: code
- name: enable
- name: id
- name: project_id
- name: source_sso_channel
- name: target_sso_channel
```

```ground:relation
type: EQUI_JOIN
left: cust_project_pushcust.project_id
right: tenant_project.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-project-code-schema
```
