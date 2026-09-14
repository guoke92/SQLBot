---
type: caliber
title: 服务已到期
page_key: service_expired
domain: CA证书收费
status: draft
aliases: [service_end < 今日, 已过期服务]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
belong: calibers
---

# 服务已到期

## 业务定位

以[[tables/ca_fee_company]]的 `service_end < CURDATE()` 判定，表示服务周期已过截止日（因服务截止日含当日，`service_end = 今日` 仍属[[calibers/in_service_period]]）。与[[calibers/in_service_period]]严格互补，与[[calibers/expiring_soon]]在 7 天窗口上存在语义重叠（本口径只看已过期，不看到期前的提醒窗口）。

服务到期处理会关闭 RENEW 待缴单并将企业置为 `UNPAID`（见[[processes/ca_fee_company_pay_status]]与[[rules/renew_remind_rule]]）。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 服务已到期
predicate: "ca_fee_company.service_end < CURDATE()"
scope: ca_fee_company
evidence: code
```