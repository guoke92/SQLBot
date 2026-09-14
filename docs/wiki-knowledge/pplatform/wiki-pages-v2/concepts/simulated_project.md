---
type: concept
title: 模拟立项
page_key: simulated_project
domain: 项目报表/统计/上报
status: draft
aliases:
  - 模拟立项
  - MANUAL
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.java:DATA_SOURCE_MANUAL
contract_version: "0.1"
maps_to: "wechat_project_approval_apply.data_source='MANUAL'"
field_targets:
  - wechat_project_approval_apply.data_source
adjudication: boundary
also_confused_with:
  - 真实立项
belong: concepts
sources: ["enrich:wiki-admin"]
---

「模拟立项」指不经过企微审批、由页面手工制造出来的立项数据，其判定字段是 [[tables/wechat_project_approval_apply|wechat_project_approval_apply]].data_source='MANUAL'，并常伴随以 MN 开头的 spNo。统计与提醒若不加区分，会把模拟数据算进真实业务量，因此在分析、导出与提醒场景都要求显式声明是否包含模拟立项。

## 需求背景

需求文档中出现「模拟立项」与「MANUAL」两种称法，本页判定为同一概念；它与[[concepts/real_project|真实立项]]之间是边界关系（adjudication=boundary），由 data_source 字段值区分，而非由单号前缀单独决定。

## 版本演进

v0 契约首版。边界：模拟立项 spNo 以 MN 开头、data_source=MANUAL；真实立项 data_source=WECHAT。见 [[processes/data_source|数据来源状态机]]。

相关：[[wechat_project_approval_apply]]
