---
type: process
title: "项目上线审批工作流"
page_key: "process/project_online_approval_workflow"
domain: "tenant-project"
status: published
aliases: ["审批工作流状态机"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

项目上线审批工作流描述审批主记录从待发起、运行中到完成或终止的状态流转，字段为 `tenant_project_approval.wf_status`。

## 需求背景
状态机基于 [代码] 枚举与转换逻辑提取，覆盖草稿暂存、工作流启动、完成/终止及重新发起等场景。

## 版本演进
v0.1 版本基于语义分析 [代码] 证据建立，后续需补充需求文档确认事件业务含义。

```ground:state_machine
name: "项目上线审批工作流"
field: "tenant_project_approval.wf_status"
states:
  - value: "PENDING"
    label: "待发起/待审批"
    source: "code_enum"
  - value: "RUNNING"
    label: "运行中"
    source: "code_enum"
  - value: "FINISHED"
    label: "已完成"
    source: "code_enum"
  - value: "TERMINATED"
    label: "已终止"
    source: "code_enum"
transitions:
  - from: "__any__"
    event: "create_initial_approval"
    to: "PENDING"
    evidence: "code_path:ProjectApprovalApplication.java:createInitialApproval -> save with wfStatus PENDING"
  - from: "PENDING"
    event: "submit_draft"
    to: "PENDING"
    evidence: "code_path:ProjectApprovalApplication.java:submit -> isDraft=Y 仅落库不启动工作流"
  - from: "PENDING"
    event: "start_workflow"
    to: "RUNNING"
    evidence: "code_path:ProjectApprovalApplication.java:startWorkflowAndUpdateStatus"
  - from: "RUNNING"
    event: "workflow_finish"
    to: "FINISHED"
    evidence: "code_path:ProjectApprovalApplication.java:handleFlowAndNodeStatus -> wfStatus FINISHED"
  - from: "RUNNING"
    event: "workflow_terminate"
    to: "TERMINATED"
    evidence: "code_path:ProjectApprovalApplication.java:handleFlowAndNodeStatus -> wfStatus TERMINATED"
  - from: "__any__"
    event: "recreate_approval"
    to: "PENDING"
    evidence: "code_path:ProjectApprovalApplication.java:doCreateApproval -> new approval wfStatus PENDING"
```

相关：[[tenant_project_approval]] [[approval_in_progress]] [[create_project_auto_create_approval_draft]] [[approval_submit_only_pending]]