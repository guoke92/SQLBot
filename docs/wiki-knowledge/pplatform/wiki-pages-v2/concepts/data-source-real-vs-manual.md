---
type: concept
title: 真实立项与模拟立项（data_source）
page_key: data-source-real-vs-manual
domain: 微企链立项与项目审批
status: draft
aliases:
  - 模拟立项
  - WECHAT/MANUAL
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
  - code_path:ProjectStatisticsApplication.java#manualCreate
contract_version: "0.1"
maps_to:
  - wechat_project_approval_apply.data_source
field_targets:
  - table: wechat_project_approval_apply
    field: data_source
adjudication: data_source='WECHAT' 表示由企微同步来的真实立项，'MANUAL' 表示人工创建的模拟立项（模拟立项创建时项目阶段固定写 IMPLEMENTATION）。导出链路固定只取 WECHAT，模拟立项不会被导出。
also_confused_with:
  - act_procinst_status（审批实例状态，与数据来源是两个维度）
sources: ["enrich:wiki-admin"]
belong: concepts
---

同一张立项申请表里混着两类业务性质不同的数据，区分它们的唯一依据就是 `data_source`。模拟立项的用途是让统计与流程可以在缺少真实企微审批的情况下先跑起来，但它并不代表真实业务事实。

判断影响面时要把这条与导出范围连起来看：[[calibers/wechat-approval-export-scope]] 固定过滤 `WECHAT`，因此任何「导出里没有某条立项」的问题，先要确认它是不是模拟数据。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 模拟立项创建固定写 `IMPLEMENTATION`，见 [[processes/project-phase]]。

相关页面：[[tables/wechat_project_approval_apply]]、[[calibers/wechat-approval-export-scope]]。

相关：[[wechat_project_approval_apply]]
