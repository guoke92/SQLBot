---
type: caliber
title: 正在审批的最新流程
page_key: running_latest_approval
domain: 微企链立项与项目审批
status: draft
aliases:
  - 审批中最新流程定位
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectBusinessConfigApplication.java:findRunningApproval
contract_version: "0.1"
belong: calibers
---

业务系统推送项目配置时，用于定位「当前正在生效的那一次上线审批」的口径：状态为审批中、且为最新版本、且启用。

```ground:caliber
name: 正在审批的最新流程
predicate: tenant_project_approval.wf_status = 'RUNNING' AND tenant_project_approval.is_latest = 'Y' AND tenant_project_approval.enable = 'Y'
scope: 业务系统推送项目配置时定位审批中流程
evidence: code_path:ProjectBusinessConfigApplication.java:findRunningApproval
```

## 需求背景

重新发起审批时原记录 `is_latest` 置 N、新记录置 Y，因此「最新版本」是区分多次审批的关键维度，见 [[rules/reinitiate_online_approval_copy]]；该口径与节点口径 [[calibers/approving_flow_node]] 联合决定推送是否落库，见 [[rules/business_config_push_node_check]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。