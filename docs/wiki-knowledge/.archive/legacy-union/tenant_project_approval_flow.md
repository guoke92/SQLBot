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
title: 审批流程节点表（提交时先删后增重建，每节点一行）。
page_key: tenant_project_approval_flow
domain: 项目审批
aliases:
- tenant_project_approval_flow
anchors:
- tenant_project_approval_flow
---
# tenant_project_approval_flow

审批流程节点表（提交时先删后增重建，每节点一行）。

```ground:table
table: tenant_project_approval_flow
description: 审批流程节点表（提交时先删后增重建，每节点一行）。
inactive: false
fields:
- name: approver_user_id
- name: node_code
- name: node_name
- name: node_order
- name: node_status
  dictionary: node-status
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow.ref_tenant_project_approval_flow_tenant_project_approval
right: tenant_project_approval.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-submit
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval_flow
right: tenant_project_approval_flow.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-desk
```
