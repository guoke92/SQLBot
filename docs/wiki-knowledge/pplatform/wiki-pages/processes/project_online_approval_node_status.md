---
type: process
title: "项目上线审批节点状态"
page_key: project_online_approval_node_status
belong: processes
domain: "tenant-project"
status: published
aliases: ["审批节点状态机"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

项目上线审批节点状态描述审批节点从待审批、审批中到已审批或拒绝的状态流转，字段为 `tenant_project_approval_flow.node_status`。

## 需求背景
状态机基于 [代码] 枚举与监听器逻辑提取，覆盖待办通知、通过、退回与驳回等事件。

## 版本演进
v0.1 版本基于语义分析 [代码] 证据建立，后续需补充需求文档确认事件业务含义。

```ground:state_machine
name: "项目上线审批节点状态"
field: "tenant_project_approval_flow.node_status"
states:
  - value: "PENDING"
    label: "待审批"
    source: "code_enum"
  - value: "APPROVING"
    label: "审批中"
    source: "code_enum"
  - value: "APPROVED"
    label: "已审批"
    source: "code_enum"
  - value: "REJECTED"
    label: "已拒绝"
    source: "code_enum"
transitions:
  - from: "PENDING"
    event: "todo_notice"
    to: "APPROVING"
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate -> APPROVING"
  - from: "APPROVING"
    event: "task_pass"
    to: "APPROVED"
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate -> APPROVED"
  - from: "APPROVING"
    event: "task_back"
    to: "PENDING"
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate -> PENDING"
  - from: "APPROVING"
    event: "task_reject"
    to: "REJECTED"
    evidence: "code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate -> REJECTED"
```

相关：[[tenant_project_approval_flow]] [[approval_running_config_receivable]] [[formal_submit_requires_valid_nodes_and_files]]