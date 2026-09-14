---
type: concept
title: 真实立项
page_key: real_project
domain: 项目报表/统计/上报
status: draft
aliases:
  - 真实立项
  - WECHAT
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:dataSourceToChinese
contract_version: "0.1"
maps_to: "wechat_project_approval_apply.data_source='WECHAT'"
field_targets:
  - wechat_project_approval_apply.data_source
adjudication: boundary
also_confused_with:
  - 模拟立项
belong: concepts
sources: ["enrich:wiki-admin"]
---

「真实立项」指经企微审批流回流、具备真实审批实例的立项数据，判定字段为 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]].data_source='WECHAT'。只有真实立项才具备可信的审批状态（act_procinst_status）与阶段流转语义，[[rules/project_phase_linkage|项目阶段联动]] 等自动流转也建立在这一前提上。

## 需求背景

需求文档以「真实立项」与「WECHAT」指代同一概念；与[[concepts/simulated_project|模拟立项]]之间为边界关系，边界由 data_source 取值确定。

## 版本演进

v0 契约首版。边界：来自企微审批的真实数据（data_source=WECHAT），可与审批通过状态（act_procinst_status='2'）联合使用，见 [[processes/act_procinst_status|企微审批状态状态机]]。

相关：[[wechat_project_approval_apply]]
