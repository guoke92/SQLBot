---
type: concept
title: 运营对接人
page_key: op_contact
domain: 微企链立项与项目审批
status: draft
aliases:
  - op_contact
  - operation_id
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java:validateAndImportData
contract_version: "0.1"
maps_to: wechat_project_approval_apply.op_contact
field_targets:
  - wechat_project_approval_apply.op_contact
adjudication: synonym
also_confused_with: []
belong: concepts
field_targets: [wechat_project_approval_apply.op_contact]
---

「运营对接人」在库中以 `operation_id` 形式存储，页面展示时反查姓名，因此同一个业务概念在存储值与展示值上写法不同。

## 需求背景

企微审批导入时，运营对接人（连同风控对接人）在校验通过并更新后，至少一列有值即触发下游同步，见 [[rules/wechat_approval_import_update_only]]。字段所在表见 [[wechat_project_approval_apply]]。

## 版本演进

当前语义分析未提供该术语的历史变更记录。