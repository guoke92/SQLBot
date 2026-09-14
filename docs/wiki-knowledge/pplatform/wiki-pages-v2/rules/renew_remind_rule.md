---
type: rule
title: 续费提醒规则
page_key: renew_remind_rule
domain: CA证书收费
status: draft
aliases: [caFeeRenewalTodoJob, 续费待办规则]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeScheduledJobHandler.java:caFeeRenewalTodoJob
contract_version: "0.1"
belong: rules
---

# 续费提醒规则

## 业务定位

企业 `service_end` 距今 **≤7 天** 且 `renew_remind_sent='N'` 时：生成 **RENEW 待缴订单**并发送续费待办，随后把 `renew_remind_sent` 置为 `'Y'`。

这是一条**定时任务驱动**的规则（`caFeeRenewalTodoJob`），服务期临近截止时自动触发续费动作。`renew_remind_sent` 起到幂等闸的作用，保证同一周期只生成一次；该标记在服务到期处理时会被复位，见[[processes/ca_fee_renew_remind]]。触发集合口径见[[calibers/expiring_soon]]，待办术语见[[concepts/todo]]，字段见[[tables/ca_fee_company]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

触发续费订单和提醒。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 续费提醒规则
content: 企业 service_end 距今 ≤7 天且 renew_remind_sent='N' 时，生成 RENEW 待缴订单并发送续费待办，随后置 renew_remind_sent='Y'。
impact: 触发续费订单和提醒。
field_targets: [ca_fee_company.service_end, ca_fee_company.renew_remind_sent]
evidence: "code_path:CaFeeScheduledJobHandler.java:caFeeRenewalTodoJob"
```