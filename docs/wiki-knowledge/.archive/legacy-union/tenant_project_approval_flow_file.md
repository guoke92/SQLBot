---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-approval@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 审批文件。
page_key: tenant_project_approval_flow_file
domain: 项目管理
aliases:
- tenant_project_approval_flow_file
anchors:
- tenant_project_approval_flow_file
---
# tenant_project_approval_flow_file

审批文件。

```ground:table
table: tenant_project_approval_flow_file
description: 审批文件。
inactive: false
fields:
- name: code
- name: enable
- name: id
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval
right: tenant_project_approval.code
cardinality: n_to_1
status: proposed
evidence: code_path:ev-approval-workflow
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_file.ref_tenant_project_approval_flow_file_project_approval_flow_node
right: tenant_project_approval_flow_node.code
cardinality: n_to_1
status: proposed
evidence: code_path:ev-approval-workflow
```
