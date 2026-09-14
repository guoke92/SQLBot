---
type: concept
title: 数据来源
page_key: data_source
domain: 微企链立项与项目审批
status: draft
aliases:
  - data_source
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:ProjectStatisticsApplication.java:manualCreate
contract_version: "0.1"
maps_to: wechat_project_approval_apply.data_source
field_targets:
  - wechat_project_approval_apply.data_source
adjudication: synonym
also_confused_with: []
belong: concepts
field_targets: [wechat_project_approval_apply.data_source]
sources: ["enrich:wiki-admin"]
---

「数据来源」区分一条立项申请是手工模拟产生还是由企微同步产生：MANUAL 表示模拟立项，WECHAT 表示真实立项。

## 需求背景

模拟立项时该字段被强制写为 MANUAL 并由后端生成审批编号，见 [[rules/manual_create_project_apply]]；企微审批导出要求该字段为 WECHAT，见 [[calibers/wechat_approval_export]]。因此该字段是判断「这条记录是否属于真实企微业务」的首要标志。

## 版本演进

当前语义分析未提供该术语的历史变更记录。

相关：[[wechat_project_approval_apply]]
