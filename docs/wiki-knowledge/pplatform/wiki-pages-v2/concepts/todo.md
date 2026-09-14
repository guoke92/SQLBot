---
type: concept
title: 待办
page_key: todo
domain: CA证书收费
status: draft
aliases: [todo, notice, 提醒]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeMessageGateway.java
contract_version: "0.1"
maps_to: CaFeeMessageGateway.sendTodoForOrder / completeNoticeForOrder
field_targets: []
adjudication: synonym
also_confused_with: [站内信, 邮件]
belong: concepts
---

# 待办

## 业务定位

**待办**指 CA 服务费场景下通过消息网关发送的**通知任务**，覆盖缴费、续费、到期等节点，由 `CaFeeMessageGateway` 的 `sendTodoForOrder` 下发、`completeNoticeForOrder` 完结。它是业务动作（提请缴费、催续费、告知到期）在系统内的可追踪载体。

**同义词**：`todo`、`notice`、`提醒`。

**易混边界**：待办 ≠ **站内信**、≠ **邮件**。后两者是**送达渠道**，待办是**业务任务语义**；同一待办可以经不同渠道触达，讨论时请区分"发了什么待办"与"用什么通道发"。

待办生成与复位的状态标记见[[tables/ca_fee_company]]的 `renew_remind_sent` 及状态机[[processes/ca_fee_renew_remind]]；触发条件见[[rules/renew_remind_rule]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自代码调用点。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。