---
type: rule
title: 统计口径固定金融科技业务
page_key: rule/sp-type-fintech-scope
domain: 微企链立项与项目审批
status: draft
aliases:
  - sp_type 固定取值
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
contract_version: "0.1"
---

项目统计的取数范围被固定为业务类型等于「金融科技业务」，即 `sp_type='金融科技业务'`。该条件不由前端控制，属于统计口径的一部分。

因此统计页显示的项目数与导出范围（见 [[calibers/wechat-approval-export-scope]]）并不等价：两者过滤的是不同维度。字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 统计口径固定金融科技业务
subject: wechat_project_approval_apply.sp_type
evidence: code
source_meaning: 业务类型；统计口径固定 sp_type='金融科技业务'
```