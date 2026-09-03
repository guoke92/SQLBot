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
title: 业务系统（讯易链/线上保理/订单融资）在审批中推送的运营配置（仅方案经理/方案配置 节点 APPROVING 时接受落库，否则静默丢弃）。
page_key: tenant_project_approval_business_info
domain: 项目审批
aliases:
- tenant_project_approval_business_info
anchors:
- tenant_project_approval_business_info
---
# tenant_project_approval_business_info

业务系统（讯易链/线上保理/订单融资）在审批中推送的运营配置（仅方案经理/方案配置 节点 APPROVING 时接受落库，否则静默丢弃）。

```ground:table
table: tenant_project_approval_business_info
description: 业务系统（讯易链/线上保理/订单融资）在审批中推送的运营配置（仅方案经理/方案配置 节点 APPROVING 时接受落库，否则静默丢弃）。
inactive: false
fields:
- name: attachment_json
- name: product_code
- name: ref_tenant_project_approval_business_info_project_approval
- name: source_system
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval
right: tenant_project_approval.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-bizinfo
```
