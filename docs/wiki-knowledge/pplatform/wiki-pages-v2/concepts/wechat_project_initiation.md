---
type: concept
title: 微企链立项
page_key: wechat_project_initiation
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
    - tenant_project
sources:
  - db:wechat_project_approval_apply
  - db:tenant_project_approval
contract_version: "0.1"
maps_to: wechat_project_approval_apply
field_targets:
  - wechat_project_approval_apply.sp_no
  - tenant_project_approval.sp_no
adjudication: boundary
also_confused_with:
  - tenant_project_approval
belong: concepts
---

「微企链立项」在业务口语中指企微（企业微信）侧提交的项目立项审批申请，落库在 [[wechat_project_approval_apply]]，与产融平台的「项目上线审批」是两个不同概念。

## 需求背景

两者通过 `sp_no`（审批编号）关联，但表不同、状态字段不同、审批主体不同：微企链立项关注企微审批实例是否通过，项目上线审批关注平台工作流是否走完。术语混用会直接导致口径取错——例如把企微审批状态当作工作流状态过滤，参见 [[concepts/approval_status]]。微企链立项侧的数据来源区分手工模拟与企微同步，见 [[concepts/data_source]]。

## 版本演进

当前语义分析未提供该术语的历史变更记录。