---
type: caliber
title: 企微立项审批导出范围
page_key: caliber/wechat-approval-export-scope
domain: 微企链立项与项目审批
status: draft
aliases:
  - 导出固定过滤
  - exportWechatApprovalInfo 口径
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo
contract_version: "0.1"
---

导出接口的取数范围由两个固定条件决定：审批实例状态必须是通过（`'2'`），数据来源必须是企微同步（`WECHAT`）。这一条同时排除了两类数据——未通过的立项审批，以及人工创建的模拟立项。

实现上的关键点是：固定条件写在动态条件之后，且前端入参不可改写，也就是说用户在前端选什么都没法把模拟立项或未通过审批带出来。相关字段语义见 [[tables/wechat_project_approval_apply]]，模拟立项与真实立项的区分见 [[concepts/data-source-real-vs-manual]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该口径的历史变更记录。

```ground:caliber
name: 企微立项审批导出范围
predicate: "wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.data_source = 'WECHAT'"
scope: 导出接口 /cust-web/wechatApproval/export，固定过滤写在动态条件之后，前端入参不可改写
evidence: "code_path:WechatProjectApprovalApplication.java#exportWechatApprovalInfo"
```