---
type: concept
title: 审批状态
page_key: approval_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - act_procinst_status
  - wf_status
oid: 1
scope:
  databases:
    - wechat_project
    - tenant_project
sources:
  - db:wechat_project_approval_apply
  - db:tenant_project_approval
contract_version: "0.1"
maps_to: wechat_project_approval_apply.act_procinst_status
field_targets:
  - wechat_project_approval_apply.act_procinst_status
  - tenant_project_approval.wf_status
  - tenant_project_approval_flow.node_status
adjudication: boundary
also_confused_with:
  - tenant_project_approval.wf_status
belong: concepts
field_targets: [wechat_project_approval_apply.act_procinst_status]
sources: ["enrich:wiki-admin"]
---

「审批状态」是一个被多套状态字段共享的模糊叫法，必须按表拆开理解：`act_procinst_status` 是企微审批实例状态（数值型 1/2），`wf_status` 是产融平台项目上线审批工作流状态（枚举字符串），`node_status` 是流程节点状态。

## 需求背景

三者取值域与流转规则都不同，参见 [[processes/wechat_apply_approval_status]]、[[processes/tenant_project_approval_wf_status]] 与 [[processes/tenant_project_approval_flow_node_status]]。混用的典型后果是把「企微已通过」当成「平台审批通过」，从而错误触发导出、统计或项目生效逻辑。为减少歧义，页面与规则中应始终写明具体字段名。

## 版本演进

当前语义分析未提供该术语的历史变更记录。

相关：[[wechat_project_approval_apply]]
