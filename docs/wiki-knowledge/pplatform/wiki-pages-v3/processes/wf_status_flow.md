---
type: process
title: 上线审批工作流状态机
page_key: wf_status_flow
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
  - tenant_project_approval.wf_status
---

创建 PENDING（待发起）→ 启动 RUNNING → 通过 FINISHED 或拒绝 TERMINATED。FINISHED 会生效项目。

```ground:process
name: 上线审批工作流状态机
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起
    source: code_enum
  - value: RUNNING
    label: 审批中
    source: code_enum
  - value: FINISHED
    label: 审批通过
    source: code_enum
  - value: TERMINATED
    label: 审批拒绝
    source: code_enum
transitions:
  - from: PENDING
    event: 启动工作流
    to: RUNNING
    evidence: "code_path:ProjectApprovalApplication.java:695"
  - from: RUNNING
    event: 审批通过
    to: FINISHED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:227"
  - from: RUNNING
    event: 审批拒绝或退回
    to: TERMINATED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:230"
```
