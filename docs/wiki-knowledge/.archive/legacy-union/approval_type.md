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
type: enum
title: 审批类型
page_key: approval_type
domain: 项目审批
aliases:
- 上线审批
- 后补协议
anchors:
- approval_type
---
# 审批类型

flow_node 按 approval_type 分域：ONLINE_APPROVAL 项目上线审批 与 BACK_AGREEMENT 后补合作协议（共用流水表，nodeOrder 各自从 1 递增）。 狭义"上线审批"指 ONLINE_APPROVAL。

```ground:enum
enum: approval_type
fields:
- tenant_project_approval_flow_node.approval_type
values:
  ONLINE_APPROVAL:
    label: 项目上线审批
  BACK_AGREEMENT:
    label: 后补合作协议
```

## 关联
- [[tenant_project_approval_flow_node|tenant_project_approval_flow_node]]
