---
type: process
title: 企微立项审批状态
page_key: wechat_apply_approval_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - act_procinst_status
  - 企微审批实例状态
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
belong: processes
---

[[wechat_project_approval_apply]] 上的企微审批实例状态字段，描述单条立项申请在企微审批实例中的推进结果。它是「业务是否可以往下走」的闸门：导出只取已通过记录，统计导入跳过审批中记录。注意它与平台侧工作流状态是两套口径，不要混用，参见 [[concepts/approval_status]]。

```ground:process
name: 企微立项审批状态
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: '1'
    label: 审批中
    source: code_const
  - value: '2'
    label: 已通过
    source: code_const
  - value: '3'
    label: 未知
    source: db_dist
  - value: '4'
    label: 未知
    source: db_dist
transitions: []
```

## 需求背景

状态 `2`（已通过）是企微审批导出与项目阶段推进的前置条件：导出固定取已通过且来源为企微的记录，见 [[calibers/wechat_approval_export]] 与 [[rules/wechat_approval_export_hard_filter]]；统计导入时审批中的记录会被跳过，见 [[calibers/approving_apply_records]]；首笔落地时间在审批通过后更新会联动项目阶段，见 [[rules/project_phase_auto_transition]]。

## 版本演进

代码常量仅显式声明 1、2 两个取值，而 DB 分布中存在 3、4，语义未知，未在代码中出现对应分支。