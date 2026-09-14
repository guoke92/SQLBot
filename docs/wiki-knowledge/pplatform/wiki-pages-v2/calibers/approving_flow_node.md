---
type: caliber
title: 正在审批的节点
page_key: approving_flow_node
domain: 微企链立项与项目审批
status: draft
aliases:
  - 审批中节点定位
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectBusinessConfigApplication.java:findApprovingFlow
contract_version: "0.1"
belong: calibers
---

业务系统推送项目配置时，用于定位「当前审批中节点」的口径：节点状态为审批中且节点启用。

```ground:caliber
name: 正在审批的节点
predicate: tenant_project_approval_flow.node_status = 'APPROVING' AND tenant_project_approval_flow.enable = 'Y'
scope: 业务系统推送项目配置时定位当前节点
evidence: code_path:ProjectBusinessConfigApplication.java:findApprovingFlow
```

## 需求背景

节点状态取值见 [[processes/tenant_project_approval_flow_node_status]]，所在表见 [[tenant_project_approval_flow]]；只有该口径命中且节点类型为方案经理或项目配置时，推送才会落库，见 [[rules/business_config_push_node_check]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。