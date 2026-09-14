---
type: rule
title: 项目上线审批提交规则
page_key: online_approval_submit
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:submit
contract_version: "0.1"
belong: rules
---

区分「暂存」与「提交」两种动作的准入规则：暂存只落库，提交才校验并启动工作流。

```ground:rule
name: 项目上线审批提交规则
content: isDraft=Y 暂存仅落库不启动工作流；isDraft=N 提交时校验审批流程节点（除方案配置外审批人必填）、必须上传商务批复报价文件，生成审批编号后启动工作流。
impact: 保证上线审批数据完整并驱动工作流。
field_targets:
  - tenant_project_approval.wf_status
  - tenant_project_approval.sp_no
evidence: code_path:ProjectApprovalApplication.java:submit
```

## 需求背景

提交成功后审批进入 `PENDING` 并由启动工作流推进到 `RUNNING`，见 [[processes/tenant_project_approval_wf_status]]；必传的商务批复报价文件属于影像分类范围，见 [[tenant_project_approval_flow_file]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。