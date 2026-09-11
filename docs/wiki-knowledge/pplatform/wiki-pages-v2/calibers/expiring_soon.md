---
type: caliber
title: 即将到期
page_key: calibers/expiring_soon
domain: CA证书收费
status: draft
aliases: [7天内到期, renew_remind_sent=N 待提醒]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 即将到期

## 业务定位

以[[tables/ca_fee_company]]的 `service_end <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)` **且** `renew_remind_sent='N'` 判定，即"7 天内到期且本期续费待办尚未生成"。它同时是[[rules/renew_remind_rule|续费提醒规则]]的触发条件与续费待办生成的工作队列口径。

**使用注意**：本口径内含 `renew_remind_sent='N'`，只适用于"待推送提醒"的场景；若业务想统计"所有 7 天内到期的企业"（不论是否已提醒），需去掉后半个条件另行定义。提醒生成后该企业即退出本口径，状态流转见[[processes/ca_fee_renew_remind]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 即将到期
predicate: "ca_fee_company.service_end <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND ca_fee_company.renew_remind_sent = 'N'"
scope: ca_fee_company
evidence: code
```