---
type: rule
title: 文本字段长度上限
page_key: import-length-limits
domain: 微企链立项与项目审批
status: draft
aliases:
  - 备注长度限制
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectStatisticsApplication.java
  - code_path:WechatProjectApprovalApplication.java
contract_version: "0.1"
belong: rules
---

同一列在不同导入路径下的长度上限并不相同：`comment`（备注）企微导入上限 200 字、项目立项统计导入上限 500 字；`custom_field_one` 长度校验 500；`project_exception_remark` 统计导入 ≤500 字。

这意味着「同一条备注为什么在另一条路径上被拒」是预期行为，排查时应先确认走的是哪条导入链路。字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 文本字段长度上限
subject: wechat_project_approval_apply.comment
evidence: code
source_meaning: 备注；企微导入上限 200 字，项目立项统计导入上限 500 字
```