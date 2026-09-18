---
type: rule
title: 工作台同意不等于审批通过
page_key: approval_desk_does_not_finish_wf
belong: rules
domain: tenant
status: draft
field_targets: [tenant_project_approval.wf_status, tenant_project_approval_flow.node_status]
sources: ['code_path:ProjectApprovalDeskApplication.java:94']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval, tenant_project_approval_flow]
---

# 工作台同意不等于审批通过

agree/back/reject 写节点状态。wf_status=FINISHED/TERMINATED 由流程结束监听写入。
催办只发企微，不改这两列。


```ground:rule
rule: 工作台同意不等于审批通过
field_targets: [tenant_project_approval.wf_status, tenant_project_approval_flow.node_status]
impact: write_constraint
content: 'agree/back/reject 写节点状态。wf_status=FINISHED/TERMINATED 由流程结束监听写入。

  催办只发企微，不改这两列。

  '
evidence: code_path:ProjectApprovalDeskApplication.java:94
```

## 页面链接

- [[tables/tenant_project_approval]]
- [[tables/tenant_project_approval_flow]]
- [[dicts/tenant_project_approval__wf_status]]
- [[dicts/tenant_project_approval_flow__node_status]]
- [[processes/tenant_project_approval__wf_status]]
