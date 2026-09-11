---
type: process
title: 企微立项审批实例状态
page_key: process/wechat_project_approval_apply_act_procinst_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - act_procinst_status
  - 企微审批实例状态
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
  - code_path:ProjectApprovalApplication.java#listProjectSpNo
contract_version: "0.1"
---

严格来说这不是一个由本系统驱动的状态机，而是对企微侧审批实例状态的镜像登记：[[tables/wechat_project_approval_apply]] 的 `act_procinst_status` 保存的是从企微同步过来的实例状态。本系统代码只声明并使用了其中一个字面值——`'2'` 表示审批通过，导出链路与立项审批编号下拉都固定过滤 `'2'`（见 [[calibers/wechat-approval-export-scope]]、[[calibers/project-sp-no-options]]）。

其余取值 `'1'`、`'3'`、`'4'` 仅出现在 DB 分布中，代码里没有对应的字面或标签，因此它们的业务含义在本层不可判定，任何针对它们的解释都属于推测。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 该列的状态语义长期只用到 `'2'`，其余取值缺少代码标签，属待补语义（见文末 REVIEW）。

```ground:process
name: 企微立项审批状态
field: wechat_project_approval_apply.act_procinst_status
states:
  - value: "1"
    label: 代码未声明（DB 分布值）
    source: db_dist
  - value: "2"
    label: 审批通过（代码固定过滤字面 '2'）
    source: code_enum
  - value: "3"
    label: 代码未声明（DB 分布值）
    source: db_dist
  - value: "4"
    label: 代码未声明（DB 分布值）
    source: db_dist
transitions: []
```