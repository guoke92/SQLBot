---
type: rule
title: 项目阶段自动流转规则
page_key: project_phase_auto_transition
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
contract_version: "0.1"
belong: rules
---

项目阶段随业务进展自动推进的规则：审批通过后首笔落地时间被更新即进入持续运营。

```ground:rule
name: 项目阶段自动流转规则
content: 审批通过后，若首笔落地时间被更新且项目阶段不是持续运营，则自动将项目阶段置为 OPERATION（持续运营）。
impact: 项目阶段随业务进展自动推进。
field_targets:
  - wechat_project_approval_apply.project_phase
  - wechat_project_approval_apply.first_settlement_time
  - wechat_project_approval_apply.act_procinst_status
evidence: code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
```

## 需求背景

触发条件中的「审批已通过」即企微审批实例状态为已通过，见 [[processes/wechat_apply_approval_status]]；阶段取值与遗留值归一见 [[processes/project_phase]]；首笔落地时间字段语义见 [[wechat_project_approval_apply]]。

## 版本演进

规则随项目阶段取值域收敛而稳定：历史值 `TERMINATION` 已归一为 `HANG`，因此本规则只需排除「已是持续运营」的情形。