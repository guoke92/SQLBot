---
type: rule
title: 审批通过生效项目
page_key: effective_project_on_approval_finished
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished
contract_version: "0.1"
belong: rules
---

上线审批走到终态后自动把关联项目置为生效，实现项目生效的自动化。

```ground:rule
name: 审批通过生效项目
content: 上线审批终态为 FINISHED 时，将审批关联的项目置为已生效（effective），并推送业务系统。
impact: 项目生效自动化。
field_targets:
  - tenant_project.project_status
  - tenant_project_approval.wf_status
evidence: code_path:ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished
```

## 需求背景

触发条件是工作流状态进入 `FINISHED`，见 [[processes/tenant_project_approval_wf_status]]；生效后项目状态发生变化，会影响「可发起上线审批的项目」口径，见 [[calibers/selectable_projects_for_online_approval]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。