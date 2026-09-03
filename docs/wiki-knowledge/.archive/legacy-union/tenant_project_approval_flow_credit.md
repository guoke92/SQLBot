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
title: 审批授信信息。
page_key: tenant_project_approval_flow_credit
domain: 项目管理
aliases:
- tenant_project_approval_flow_credit
anchors:
- tenant_project_approval_flow_credit
---
# tenant_project_approval_flow_credit

审批授信信息。

```ground:table
table: tenant_project_approval_flow_credit
description: 审批授信信息。
inactive: false
fields:
- name: code
- name: enable
- name: id
- name: ref_tenant_project_approval_flow_credit_project_approval_node
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_credit.ref_tenant_project_approval_flow_credit_project_approval
right: tenant_project_approval.code
cardinality: n_to_1
status: proposed
evidence: code_path:ev-approval-workflow
```
