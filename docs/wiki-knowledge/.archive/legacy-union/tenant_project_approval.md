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
title: 项目上线审批主表（每轮审批一行，is_latest 标记最新轮，引擎视角 wf_status）。
page_key: tenant_project_approval
domain: 项目审批
aliases:
- tenant_project_approval
anchors:
- tenant_project_approval
---
# tenant_project_approval

项目上线审批主表（每轮审批一行，is_latest 标记最新轮，引擎视角 wf_status）。

```ground:table
table: tenant_project_approval
description: 项目上线审批主表（每轮审批一行，is_latest 标记最新轮，引擎视角 wf_status）。
inactive: false
fields:
- name: act_procinst_id
- name: approval_no
- name: complete_time
- name: enable
- name: initiate_time
- name: is_add
- name: is_latest
- name: is_low_risk
- name: ref_tenant_project_approval_tenant_project
- name: ref_tenant_project_approval_tenant_project_approval
- name: wf_last_operate_time
- name: wf_last_operator
- name: wf_procdef_key
- name: wf_status
  dictionary: wf-status
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.ref_tenant_project_approval_tenant_project
right: tenant_project.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-create
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
left: tenant_project_approval_flow_node.ref_tenant_project_approval_flow_node_project_approval
right: tenant_project_approval.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-desk
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval
right: tenant_project_approval.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-bizinfo
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.ref_tenant_project_approval_tenant_project_approval
right: tenant_project_approval.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-recreate
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.ref_tenant_project_approval_tenant_project_approval
right: tenant_project_approval.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-recreate
```
