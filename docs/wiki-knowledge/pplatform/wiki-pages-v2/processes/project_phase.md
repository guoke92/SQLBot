---
type: process
title: 项目阶段状态机
page_key: project_phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目阶段
  - project_phase
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
  - code_path:ProjectStatisticsApplication.java:normalizeLegacyProjectPhaseCode
contract_version: "0.1"
belong: processes
---

项目阶段描述一个立项申请从立项到实施、再到持续运营或挂起的生命周期位置，落库字段为 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]].project_phase。阶段推进不是纯人工操作：审批通过与首笔落地时间写入会触发自动流转，历史遗留值在查询时被规范化。

## 需求背景

需求文档未单独描述该状态机；本次分析的状态与迁移均来自代码常量与方法名证据。

## 版本演进

v0 契约首版。当前有两条迁移规则：一是审批通过且首笔落地时间更新时的自动置为 OPERATION（见 [[rules/project_phase_linkage|项目阶段联动]]），二是查询期把历史值 TERMINATION 规范化为 HANG。INITIATION 为立项起点，尚未观察到由代码写入的入边与出边。

```ground:process
name: 项目阶段
field: wechat_project_approval_apply.project_phase
states:
  - value: INITIATION
    label: 立项阶段
    source: code_const
  - value: IMPLEMENTATION
    label: 实施阶段
    source: code_const
  - value: OPERATION
    label: 持续运营
    source: code_const
  - value: HANG
    label: 挂起
    source: code_const
transitions:
  - from: "*"
    event: 首笔落地时间更新且审批通过
    to: OPERATION
    evidence: code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
  - from: TERMINATION
    event: 查询时规范化
    to: HANG
    evidence: code_path:ProjectStatisticsApplication.java:normalizeLegacyProjectPhaseCode
evidence: code_path:ProjectStatisticsApplication.java:applyOperationPhaseWhenFirstSettlementUpdatedUnderApproved
```