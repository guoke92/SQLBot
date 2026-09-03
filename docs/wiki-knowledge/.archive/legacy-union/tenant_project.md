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
title: 租户项目配置（本单元仅引用关联与回写字段）。
page_key: tenant_project
domain: 项目审批
aliases:
- tenant_project
anchors:
- tenant_project
---
# tenant_project

租户项目配置（本单元仅引用关联与回写字段）。

```ground:table
table: tenant_project
description: 租户项目配置（本单元仅引用关联与回写字段）。
inactive: false
fields:
- name: wechat_audit_no
```

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.ref_tenant_project_approval_tenant_project
right: tenant_project.code
cardinality: many_to_one
status: proposed
evidence: code_path:ev-poa-create
```
