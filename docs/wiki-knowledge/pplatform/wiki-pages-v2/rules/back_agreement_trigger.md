---
type: rule
title: 后补合作协议触发规则
page_key: back_agreement_trigger
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:isStartBackAgreement
contract_version: "0.1"
belong: rules
---

由审批节点属性触发的后补合作协议工作流启动规则。

```ground:rule
name: 后补合作协议触发规则
content: 业务经理节点同意且该节点记录 is_back_agreement=Y 时，启动后补合作协议工作流。
impact: 自动发起后补协议流程。
field_targets:
  - tenant_project_approval_flow_node.is_back_agreement
  - tenant_project_approval_flow_node.node_code
evidence: code_path:ProjectApprovalApplication.java:isStartBackAgreement
```

## 需求背景

判断依赖节点身份（`node_code` 标识业务经理节点）与节点上的后补协议标记，节点表见 [[tenant_project_approval_flow_node]]，节点操作见 [[processes/tenant_project_approval_flow_node_status]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。