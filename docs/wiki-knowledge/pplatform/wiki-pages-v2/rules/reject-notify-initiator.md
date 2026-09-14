---
type: rule
title: 拒绝与退回通知只发发起人
page_key: reject-notify-initiator
domain: 微企链立项与项目审批
status: draft
aliases:
  - 通知只发给 initiator_user_id
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalDeskApplication.java#doReject
  - code_path:ProjectApprovalDeskApplication.java#doBack
contract_version: "0.1"
belong: rules
---

审批被拒绝或退回时，通知的接收人是单据上的审批发起人（`initiator_user_id`，存的是 sys_user id），不包含方案经理、也不包含当前处理人。若发起人已离职或 id 失效，通知会静默丢失，排查「审批被退了但没人收到通知」时应先看这一列。

通知触发点对应工作台的驳回/退回动作，节点状态变化见 [[processes/project-approval-node-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 拒绝与退回通知只发发起人
subject: tenant_project_approval.initiator_user_id
evidence: code
source_meaning: 审批发起人 sys_user id；拒绝/退回通知只发给该人
```