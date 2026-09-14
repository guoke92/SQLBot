---
type: process
title: 项目上线审批工作流状态流转
page_key: project_approval_workflow_status
domain: 租户项目
status: draft
aliases: [项目上线审批工作流状态, tenant_project_approval.wf_status, wf_status]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
belong: processes
---

项目上线审批工作流状态位于 [[tables/tenant_project_approval]] 的 wf_status 列，描述审批实例从待发起、审批中到完成或终止的推进过程。审批完成会反向影响项目状态（[[processes/tenant_project_status]]）。节点级的处理进度见 [[processes/project_approval_node_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决三件事：①发起审批并进入审批中；②审批流结束后区分「完成」与「终止」；③已结束的审批可以复制成新的待发起记录，且草稿（isDraft=Y）可暂存不回退状态。

## 版本演进
- 已结束（FINISHED/TERMINATED）的审批通过 doCreateApproval 复制新记录回到 PENDING，说明「一个项目可多次上线审批」是既有能力。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 项目上线审批工作流状态
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起/待审批
    source: code_enum
  - value: RUNNING
    label: 审批中
    source: code_enum
  - value: FINISHED
    label: 已完成
    source: code_enum
  - value: TERMINATED
    label: 已终止
    source: code_enum
transitions:
  - from: PENDING
    event: startWorkflowAndUpdateStatus 启动工作流
    to: RUNNING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:startWorkflowAndUpdateStatus"
  - from: RUNNING
    event: handleFlowAndNodeStatus 判断为 FINISHED
    to: FINISHED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: RUNNING
    event: handleFlowAndNodeStatus 判断为 TERMINATED
    to: TERMINATED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: PENDING
    event: submit 暂存 isDraft=Y
    to: PENDING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:submit"
  - from: FINISHED/TERMINATED
    event: createApproval/doCreateApproval 复制新审批记录置 PENDING
    to: PENDING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:doCreateApproval"
```