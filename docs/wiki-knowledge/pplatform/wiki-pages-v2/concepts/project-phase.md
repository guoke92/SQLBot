---
type: concept
title: 项目阶段（projectPhase）
page_key: concept.project-phase
domain: 项目报表/统计/上报
status: draft
aliases:
  - projectPhase
  - project_phase
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
maps_to: "IMPLEMENTATION=实施阶段 / OPERATION=持续运营 / HANG=挂起 /（读时归一）TERMINATION→HANG"
also_confused_with:
  - "项目状态 project_status（项目台账：1=已生效，非 1=未生效）"
adjudication: boundary
boundary: "project_status 属项目台账维度（tenant_project），project_phase 属立项统计维度（wechat_project_approval_apply）。"
---

# 项目阶段（projectPhase）

「项目阶段」与「项目状态」都容易被简称为「项目状态」，但分属两个域：前者描述立项单据处于实施/运营/挂起，后者描述项目台账上项目是否已生效。

## 需求背景

- project_phase 作用于立项统计域（[[tables/wechat_project_approval_apply]]），是运营口径与自动流转的核心字段，流转规则见 [[processes/project-phase]]、[[rules/first-settlement-to-operation-phase]]。
- project_status 作用于项目台账域（tenant_project），取值为 1=已生效、非 1=未生效，用于台账列表与导出，不能与阶段值混用。

在报表/上报口径撰写时，出现「已生效/未生效」应指向 project_status；出现「实施/运营/挂起」应指向 project_phase。

## 版本演进

project_phase 的历史值 TERMINATION 已在读取时归一为 HANG，值域收敛为三态；项目台账的 project_status 保持二元语义，两者未做合并。