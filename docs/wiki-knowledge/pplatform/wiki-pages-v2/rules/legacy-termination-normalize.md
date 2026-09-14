---
type: rule
title: TERMINATION 读时归一为挂起
page_key: legacy-termination-normalize
domain: 微企链立项与项目审批
status: draft
aliases:
  - 项目阶段历史值归一
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java#normalizeLegacyProjectPhaseCode
contract_version: "0.1"
belong: rules
---

项目阶段的历史值 `TERMINATION` 不会被改库，而是在读取时被归一为「挂起」。因此库内与界面上的取值可能不一致，写筛选条件时若按 `TERMINATION` 直接查库、按挂起查界面，会得到不同结果。

字段语义见 [[tables/wechat_project_approval_apply]]，完整状态集见 [[processes/project-phase]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该归一化本身即为历史值收敛措施，说明 `TERMINATION` 属旧状态命名。

```ground:rule
rule: TERMINATION 读时归一为挂起
subject: wechat_project_approval_apply.project_phase
evidence: code
source_meaning: 项目阶段：IMPLEMENTATION(实施阶段)/持续运营/挂起；TERMINATION 为历史值读时归一为挂起；『立项阶段』仅用于展示与导入校验、不落库
```