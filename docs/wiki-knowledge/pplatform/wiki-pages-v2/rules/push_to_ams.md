---
type: rule
title: 推送AMS规则
page_key: push_to_ams
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:isPushToAms
contract_version: "0.1"
belong: rules
---

审批通过后是否向下游 AMS 系统推送审批信息的判定规则。

```ground:rule
name: 推送AMS规则
content: 审批通过后，若项目类型为标准项目，或项目类型为常规项目且 is_low_risk=Y，则推送审批信息至 AMS。
impact: 下游 AMS 系统同步审批结果。
field_targets:
  - tenant_project_approval.project_type
  - tenant_project_approval.is_low_risk
evidence: code_path:ProjectApprovalApplication.java:isPushToAms
```

## 需求背景

触发前置于工作流状态进入 `FINISHED`，见 [[processes/tenant_project_approval_wf_status]]；判定依赖项目类型与低风险标记，所在表见 [[tenant_project_approval]]。

## 版本演进

当前语义分析未提供该规则的历史变更记录。