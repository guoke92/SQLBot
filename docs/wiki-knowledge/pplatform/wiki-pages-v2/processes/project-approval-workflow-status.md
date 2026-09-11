---
type: process
title: 项目上线审批工作流状态机
page_key: process/tenant_project_approval_wf_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批 wf_status
  - tenant_project_approval.wf_status
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#createInitialApproval
  - code_path:ProjectApprovalApplication.java#submit
  - code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus
  - code_path:ProjectApprovalApplication.java#handleFlowAndNodeStatus
  - code_path:ProjectApprovalApplication.java#doCreateApproval
  - code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate
  - db:tenant_project_approval
contract_version: "0.1"
---

工作流状态描述的是「一次上线审批单据」的生命周期，字段落在 [[tables/tenant_project_approval]] 的 `wf_status` 上。它从「由项目创建逻辑预生成的草稿」开始，经发起后进入审批中，最终收敛到完成（通过）或终止（驳回/退回结束）；重新发起会以复制的方式开出一条新记录并把旧的置为非最新，因此状态机是沿记录序列而非沿单条记录循环的。

两个需要特别留意的点：一是状态写入与工作流引擎启动是两步，引擎启动失败会降级停留在待发起（见 [[rules/workflow-start-failure-degrade]]）；二是 DB 分布中存在代码枚举基线没有的 `REVOKED`。

节点粒度的状态请见 [[processes/project-approval-node-status]]，终态对租户项目状态的影响见 [[processes/tenant-project-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- `REVOKED`（已撤销）仅来自 DB 实际分布，代码枚举基线未声明，属待补枚举。
- 重新发起路径的前置校验要求记录为最新（`is_latest=Y`），否则抛出异常，见 [[rules/is-latest-uniqueness]]。

```ground:process
name: 项目上线审批工作流状态机
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起/草稿
    source: code_enum
  - value: RUNNING
    label: 审批中
    source: code_enum
  - value: FINISHED
    label: 审批完成（通过）
    source: code_enum
  - value: TERMINATED
    label: 审批终止（驳回/退回结束）
    source: code_enum
  - value: REVOKED
    label: 已撤销（代码枚举基线未声明，DB 实际存在）
    source: db_dist
transitions:
  - from: "—"
    event: 项目创建后生成审批记录（isAdd=Y+挡板开+产品白名单）
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#createInitialApproval"
  - from: PENDING
    event: submit(isDraft=N) 业务落库
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#submit（copySubmitFields 中 setWfStatus(PENDING)）"
  - from: PENDING
    event: 工作流启动成功 startWorkflowAndUpdateStatus
    to: RUNNING
    evidence: "code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus"
  - from: PENDING
    event: 工作流启动异常（降级，仅记 ERROR）
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#startWorkflowAndUpdateStatus（catch 分支）"
  - from: RUNNING
    event: 流程结束通知 approveResult=pass
    to: FINISHED
    evidence: "code_path:ProjectApprovalApplication.java#handleFlowAndNodeStatus + ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: RUNNING
    event: 流程结束通知 approveResult=reject/back
    to: TERMINATED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: FINISHED
    event: 重新发起 createApproval（复制原审批）
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#doCreateApproval"
  - from: PENDING
    event: 非最新记录再次重新发起
    to: PENDING
    evidence: "code_path:ProjectApprovalApplication.java#doCreateApproval（is_latest≠Y 抛异常前置校验）"
```