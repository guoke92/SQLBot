---
type: rule
title: 低风险标记由法务节点填写并回写
page_key: is-low-risk-writeback
domain: 微企链立项与项目审批
status: draft
aliases:
  - is_low_risk 回写
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
belong: rules
---

`is_low_risk` 不是发起时填写的字段，而是在法务经办节点上产生，并回写到主表供 AMS 推送判定使用。也就是说该值存在「填写前未知」的中间态，AMS 推送逻辑必须能容忍它尚未确定的情况。

字段语义见 [[tables/tenant_project_approval]]，与项目类型共同影响 AMS 的规则见 [[rules/project-type-drives-flow-and-ams]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 低风险标记由法务节点填写并回写
subject: tenant_project_approval.is_low_risk
evidence: code
source_meaning: 法务经办节点填写的『是否低风险』，回写主表供 AMS 推送判定
```