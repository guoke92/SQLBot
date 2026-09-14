---
type: table
title: 企微立项审批流程附件表
page_key: wechat_project_approval_flow_file
domain: 微企链立项与项目审批
status: draft
aliases:
  - wechat_project_approval_flow_file
  - 审批节点附件表
oid: 1
scope:
  databases:
    - lowcode_pplatform
sources:
  - db:wechat_project_approval_flow_file
contract_version: "0.1"
belong: tables
---

本表存放在企微立项审批各节点上产生的附件。本次语义分析只给出了一个字段的证据，即附件分类 `catg_id`，因此本页仅覆盖该列，不对本表的其余结构做任何推断。

`catg_id` 的关键事实是：DB 实际出现的取值（`FBP_OA_ATTACHMENT`、`FBP_OA_COMMENT_FILE`）超出了代码基线的枚举覆盖范围，属于「代码枚举未覆盖 DB 实际分布」的一类，阅读附件分类时不能只依赖代码枚举。与审批主流程的关系参见 [[tables/wechat_project_approval_apply]]、[[processes/wechat-approval-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- `catg_id` 的代码基线枚举未覆盖 DB 实际分布值，属于待收敛的枚举缺口，见文末 REVIEW。

