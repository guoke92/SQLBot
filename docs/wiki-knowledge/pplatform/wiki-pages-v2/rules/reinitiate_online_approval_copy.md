---
type: rule
title: 重新发起上线审批复制规则
page_key: reinitiate_online_approval_copy
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:doCreateApproval
contract_version: "0.1"
belong: rules
---

重新发起上线审批时，对原审批记录的复制与版本切换规则。

```ground:rule
name: 重新发起上线审批复制规则
content: 重新发起时复制原审批主记录、业务信息、流程配置和影像文件，原审批 is_latest 置 N，新审批 is_latest=Y，wf_status=PENDING。
impact: 保留历史审批版本并生成新草稿。
field_targets:
  - tenant_project_approval.is_latest
  - tenant_project_approval.wf_status
  - tenant_project_approval.ref_tenant_project_approval_tenant_project_approval
evidence: code_path:ProjectApprovalApplication.java:doCreateApproval
```

## 需求背景

该规则是「正在审批的最新流程」口径成立的前提——只有最新版本才会被业务系统推送逻辑定位到，见 [[calibers/running_latest_approval]]；新审批从 `PENDING` 起步，见 [[processes/tenant_project_approval_wf_status]]；复制范围包含影像文件，见 [[tenant_project_approval_flow_file]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。