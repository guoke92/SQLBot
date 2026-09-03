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
title: 审批节点状态
page_key: node_status
domain: 项目审批
aliases:
- 节点审批
- 待审批
- 已通过节点
anchors:
- node_status
---
# 审批节点状态

tenant_project_approval_flow.node_status 节点视角状态（PENDING/APPROVING/APPROVED/REJECTED）， 与主表 wf_status 两级不同："审批通过"整单=FINISHED，节点=APPROVED。

```ground:enum
enum: node_status
fields:
- tenant_project_approval_flow.node_status
values:
  PENDING:
    label: 待审批
  APPROVING:
    label: 审批中
  APPROVED:
    label: 已通过
  REJECTED:
    label: 已拒绝
```

## 关联
- [[tenant_project_approval_flow|tenant_project_approval_flow]]
