---
type: process
title: 上线审批节点状态机
page_key: process/tenant_project_approval_flow_node_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - 上线审批节点状态
  - tenant_project_approval_flow.node_status
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate
  - code_path:ProjectApprovalDeskApplication.java#doBack
  - code_path:ProjectApprovalDeskApplication.java#doReject
  - code_path:ProjectApprovalDeskApplication.java#doTransfer
contract_version: "0.1"
---

节点状态是工作流状态的下钻粒度：单据级状态（[[processes/project-approval-workflow-status]]）表达整条审批走到哪一步，节点状态表达某个人手上的待办被推到什么程度。入库位置为 `tenant_project_approval_flow.node_status`（该表本次未提供字段级语义，见文末 REVIEW）。

值得注意的是三种「非终态写法」：工作台退回 `back` 后节点回到审批中；转审 `transfer` 后节点名不变、状态仍为审批中；流程级 `back` 会使节点落到已拒绝。工作台侧的三个动作也是「拒绝/退回通知只发给发起人」这条规则的触发源（见 [[rules/reject-notify-initiator]]）。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 撤回/退回与驳回在节点状态上表现不同（前者回审批中、后者落已拒绝），该差异属既有行为，本次无文档主张可佐证其历史。

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
    event: 待抢/待办通知（taskNoticeType 1/2）
    to: APPROVING
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 任务办理完成 approveResult=pass
    to: APPROVED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 任务办理完成 approveResult=back
    to: PENDING
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 流程结束 approveResult=reject/back
    to: REJECTED
    evidence: "code_path:ProjectOnlineProcessOperateListener.java#resolveFlowNodeStatusUpdate"
  - from: APPROVING
    event: 工作台退回 back
    to: APPROVING
    evidence: "code_path:ProjectApprovalDeskApplication.java#doBack（updateFlowNodeStatus APPROVING）"
  - from: APPROVING
    event: 工作台驳回 reject
    to: REJECTED
    evidence: "code_path:ProjectApprovalDeskApplication.java#doReject"
  - from: APPROVING
    event: 工作台转审 transfer（节点名不变）
    to: APPROVING
    evidence: "code_path:ProjectApprovalDeskApplication.java#doTransfer"
```