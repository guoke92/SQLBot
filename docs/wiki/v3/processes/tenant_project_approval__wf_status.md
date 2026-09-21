---
type: process
title: 项目上线审批工作流
page_key: tenant_project_approval__wf_status
belong: processes
domain: tenant
status: draft
anchors: [tenant_project_approval.wf_status]
field_targets: [tenant_project_approval.wf_status]
sources: ['code_path:ProjectApprovalApplication.java:392', 'code_path:ProjectApprovalApplication.java:700',
  'code_path:ProjectApprovalApplication.java:914', 'code_path:ProjectApprovalApplication.java:722',
  'code_path:ProjectOnlineProcessOperateListener.java:231']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval, tenant_project_approval_flow_node, tenant_project]
---

# 项目上线审批工作流

钉 tenant_project_approval.wf_status。创建 PENDING；发起 RUNNING 并写 act_procinst_id；
流程结束监听写成 FINISHED 或 TERMINATED，通过时副作用生效项目。
REVOKED=审批撤销（发起人 revokeApproval）；勿与 TERMINATED（审批拒绝）互代。


```ground:process
process: 项目上线审批工作流
field: tenant_project_approval.wf_status
entry: POST /app-web/projectApproval
stages:
- stage: 待发起
  transitions:
  - from: PENDING
    event: createInitialApproval
    to: PENDING
    evidence: code_path:ProjectApprovalApplication.java:392
- stage: 发起
  transitions:
  - from: PENDING
    event: 启动工作流
    to: RUNNING
    evidence: code_path:ProjectApprovalApplication.java:700
  effects:
  - op: 写入流程实例
    table: tenant_project_approval
    fields: [act_procinst_id]
- stage: 撤销
  transitions:
  - from: RUNNING
    event: revokeApproval（仅发起人）
    to: REVOKED
    evidence: code_path:ProjectApprovalApplication.java:914
  - from: PENDING
    event: revokeApproval（仅发起人）
    to: REVOKED
    evidence: code_path:ProjectApprovalApplication.java:914
  effects:
  - op: 写 revoke + 撤销原因
    table: tenant_project_approval_flow_node
    fields: [operate_type]
- stage: 结束
  transitions:
  - from: RUNNING
    event: 流程结束 pass
    to: FINISHED
    evidence: code_path:ProjectApprovalApplication.java:722
  - from: RUNNING
    event: 流程结束 reject/back
    to: TERMINATED
    evidence: code_path:ProjectOnlineProcessOperateListener.java:231
  effects:
  - op: effectiveProjectOnApprovalFinished 置为已生效
    table: tenant_project
    fields: [project_status]
```

## 页面链接

- [[tables/tenant_project]]
- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow_node]]
- [[dicts/tenant_project_approval__wf_status]]
