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
title: 审批操作类型
page_key: operate_type
domain: 项目审批
aliases:
- 同意
- 驳回
- 退回
- 转审
anchors:
- operate_type
---
# 审批操作类型

flow_node 操作流水的动作类型（pass/reject/back/delegate）。

```ground:enum
enum: operate_type
fields:
- tenant_project_approval_flow_node.operate_type
values:
  pass:
    label: 同意
  reject:
    label: 驳回
  back:
    label: 退回
  delegate:
    label: 转审
```

## 关联
- [[tenant_project_approval_flow_node|tenant_project_approval_flow_node]]
