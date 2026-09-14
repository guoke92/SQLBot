---
type: rule
title: 项目阶段联动
page_key: project_phase_linkage
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目阶段联动
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
contract_version: "0.1"
belong: rules
---

当一条立项记录的审批已通过、且首笔落地时间被更新为非空时，系统把项目阶段自动置为持续运营（OPERATION）。这是一次由数据变更触发的写动作，而非页面上的显式操作，因此导入与编辑两条入口都会命中。

## 需求背景

需求文档未单列此规则；规则内容来自代码方法语义。

## 版本演进

v0 契约首版。影响面：更新/导入时触发。注意与查询期规范化（TERMINATION → HANG）的区别：后者只影响读取结果，见 [[processes/project_phase|项目阶段状态机]]。字段目标：wechat_project_approval_apply.project_phase。

```ground:rule
name: 项目阶段联动
content: 审批通过且首笔落地时间变更为非空时，项目阶段自动置为持续运营(OPERATION)
impact: 更新/导入时触发
field_targets:
  - wechat_project_approval_apply.project_phase
evidence: code_path:ProjectStatisticsApplication.applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
```