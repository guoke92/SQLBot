---
type: process
title: 续费提醒发送状态机
page_key: ca_fee_renew_remind
domain: CA证书收费
status: draft
aliases: [renew_remind_sent 状态机, 续费待办生成状态]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - code:CaFeeRenewalService.java
contract_version: "0.1"
belong: processes
---

# 续费提醒发送状态机

## 业务定位

本页描述[[tables/ca_fee_company]]中 `renew_remind_sent` 的 Y/N 两态，用于**防止同一服务周期内重复推送续费待办**：`N`（未生成）表示本期还没发过续费提醒；生成续费待办后置 `Y`（已生成）。

这是一个**可复位**的状态：服务到期处理 `markServiceExpired` 会把它从 `Y` 复位为 `N`，为下一个服务周期的提醒做准备。因此该字段不能用来判断"历史上是否发过提醒"，只能表示**当前周期是否已发**。触发条件（`service_end` 距今 ≤7 天且 `renew_remind_sent='N'`）见[[rules/renew_remind_rule]]，对应口径[[calibers/expiring_soon]]；推送通道语义见[[concepts/todo]]。

## 需求背景

本页为代码侧状态流转的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。"待办"与站内信、邮件的边界见[[concepts/todo]]。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: 续费提醒发送状态机
field: ca_fee_company.renew_remind_sent
states:
  - value: N
    label: 未生成
    source: db_dist
  - value: Y
    label: 已生成
    source: db_dist
transitions:
  - from: N
    event: 续费待办生成 markRenewRemindSent
    to: Y
    evidence: "code_path:CaFeeRenewalService.java:markRenewRemindSent"
  - from: Y
    event: 服务到期处理 markServiceExpired
    to: N
    evidence: "code_path:CaFeeRenewalService.java:markServiceExpired"
```