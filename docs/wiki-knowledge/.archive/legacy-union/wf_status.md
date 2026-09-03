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
title: 审批工作流状态
page_key: wf_status
domain: 项目审批
aliases:
- 审批通过
- 审批中
- 待发起
- 审批拒绝
- 已拒绝
anchors:
- wf_status
---
# 审批工作流状态

tenant_project_approval.wf_status 引擎视角整单状态：PENDING 待发起（草稿）→ RUNNING 审批中 → FINISHED 审批通过 / TERMINATED 审批拒绝。无撤回语义， 终态后只能重新发起新一轮。

```ground:enum
enum: wf_status
fields:
- tenant_project_approval.wf_status
values:
  PENDING:
    label: 待发起
  RUNNING:
    label: 审批中
  FINISHED:
    label: 审批通过
  TERMINATED:
    label: 审批拒绝
```

## 关联
- [[tenant_project_approval|tenant_project_approval]]
