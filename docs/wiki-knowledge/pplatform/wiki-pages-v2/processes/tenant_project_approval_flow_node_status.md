---
type: process
title: 审批流程节点状态
page_key: tenant_project_approval_flow_node_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - node_status
  - 节点状态
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval_flow
  - code_path:ProjectOnlineProcessOperateListener.java
contract_version: "0.1"
belong: processes
---

[[tenant_project_approval_flow]] 上的节点状态，随审批人在节点上的操作（同意、退回、驳回）推进，并由监听器统一解析落库。它与 [[tenant_project_approval_flow_node]] 的节点操作类型配合使用：操作类型是「做了什么」，节点状态是「节点现在处于什么状态」。

```ground:process
name: 审批流程节点状态
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
    event: 节点激活
    to: APPROVING
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
  - from: APPROVING
    event: 同意
    to: APPROVED
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
  - from: APPROVING
    event: 退回
    to: PENDING
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
  - from: APPROVING
    event: 驳回
    to: REJECTED
    evidence: code_path:ProjectOnlineProcessOperateListener.java:resolveFlowNodeStatusUpdate
```

## 需求背景

节点是否处于 `APPROVING` 是业务系统推送项目配置能否落库的判定条件，见 [[calibers/approving_flow_node]] 与 [[rules/business_config_push_node_check]]；节点上的操作类型见 [[tenant_project_approval_flow_node]] 的 `operate_type`。

## 版本演进

当前语义分析未提供该状态取值的历史变更记录。