---
type: rule
title: 待发起不是待审批
page_key: wf_pending_not_node_pending
domain: 微企链立项与项目审批
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - tenant_project_approval.wf_status
  - tenant_project_approval_flow.node_status
---

wf_status PENDING=待发起；node_status PENDING=待审批。

```ground:rule
name: 待发起不是待审批
content: wf_status PENDING=待发起；node_status PENDING=待审批。
field_targets: [tenant_project_approval.wf_status, tenant_project_approval_flow.node_status]
evidence: "code_path:ProjectApprovalWorkflowStatusEnum.java:16"
```
