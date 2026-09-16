---
type: process
title: 上线审批节点状态机
page_key: node_status_flow
domain: 微企链立项与项目审批
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets:
  - tenant_project_approval_flow.node_status
---

节点 PENDING=待审批。

```ground:process
name: 上线审批节点状态机
field: tenant_project_approval_flow.node_status
states:
  - value: PENDING
    label: 待审批
    source: code_enum
  - value: APPROVING
    label: 审批中
    source: code_enum
  - value: APPROVED
    label: 已通过
    source: code_enum
  - value: REJECTED
    label: 已拒绝
    source: code_enum
transitions:
  - from: PENDING
    event: 节点开始审批
    to: APPROVING
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:210"
  - from: APPROVING
    event: 节点通过
    to: APPROVED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:227"
  - from: APPROVING
    event: 节点拒绝
    to: REJECTED
    evidence: "code_path:ProjectApprovalDeskApplication.java:262"
```
