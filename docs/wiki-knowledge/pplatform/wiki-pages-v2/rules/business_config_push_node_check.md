---
type: rule
title: 业务系统推送项目配置节点校验
page_key: business_config_push_node_check
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectBusinessConfigApplication.java:savePush
contract_version: "0.1"
belong: rules
---

业务系统推送项目运营配置时的准入校验：只有流程与节点都处于「正确的位置」才落库。

```ground:rule
name: 业务系统推送项目配置节点校验
content: 业务系统推送项目运营配置时，仅当项目存在 wf_status=RUNNING 且 is_latest=Y 的上线审批，且当前节点为方案经理（PROJECT_MANAGER）或项目配置（PROJECT_CONFIG）且 node_status=APPROVING 时才落库更新；其他节点静默成功不落库。
impact: 控制项目配置推送时机，避免无效更新。
field_targets:
  - tenant_project_approval.wf_status
  - tenant_project_approval.is_latest
  - tenant_project_approval_flow.node_code
  - tenant_project_approval_flow.node_status
evidence: code_path:ProjectBusinessConfigApplication.java:savePush
```

## 需求背景

两个前置口径分别为 [[calibers/running_latest_approval]] 与 [[calibers/approving_flow_node]]；「最新版本」由重新发起规则维护，见 [[rules/reinitiate_online_approval_copy]]；节点状态流转见 [[processes/tenant_project_approval_flow_node_status]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。