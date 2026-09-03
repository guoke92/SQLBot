---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-online-approval@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 审批操作流水（append-only，无状态字段——状态靠 operate_type 表达）； ONLINE_APPROVAL 与 BACK_AGREEMENT
  按 approval_type 分域、nodeOrder 各自递增。
page_key: tenant_project_approval_flow_node
domain: 项目审批
aliases:
- tenant_project_approval_flow_node
anchors:
- tenant_project_approval_flow_node
---
# tenant_project_approval_flow_node

审批操作流水（append-only，无状态字段——状态靠 operate_type 表达）； ONLINE_APPROVAL 与 BACK_AGREEMENT 按 approval_type 分域、nodeOrder 各自递增。

```ground:table
table: tenant_project_approval_flow_node
description: 审批操作流水（append-only，无状态字段——状态靠 operate_type 表达）； ONLINE_APPROVAL 与 BACK_AGREEMENT
  按 approval_type 分域、nodeOrder 各自递增。
inactive: false
fields:
- name: approval_type
  dictionary: approval-type
- name: approve_comment
- name: is_back_agreement
- name: is_low_risk
- name: node_code
- name: node_order
- name: operate_time
- name: operate_type
  dictionary: operate-type
- name: operator_user_id
- name: operator_user_name
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval
right: tenant_project_approval.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-desk
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow
right: tenant_project_approval_flow.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-desk
```
