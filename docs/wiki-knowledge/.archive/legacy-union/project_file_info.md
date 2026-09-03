---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-file@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: project_file_info
page_key: project_file_info
domain: 项目管理
aliases:
- project_file_info
anchors:
- project_file_info
---
# project_file_info

project_file_info

```ground:table
table: project_file_info
description: project_file_info
inactive: false
fields:
- name: code
- name: enable
- name: file_type
- name: id
- name: name
- name: project_id
```

```ground:relation
type: EQUI_JOIN
left: project_file_info.project_id
right: tenant_project.id
cardinality: n_to_1
status: proposed
evidence: code_path:ev-project-file-schema
```
