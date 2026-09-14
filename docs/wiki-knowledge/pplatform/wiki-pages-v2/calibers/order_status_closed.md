---
type: caliber
title: 订单已关闭口径
page_key: order_status_closed
domain: CA证书收费
status: draft
aliases:
  - 已关闭订单
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerQueryService.java
contract_version: "0.1"
belong: calibers
---

订单已关闭口径指 [[ca_fee_order]] 中 `order_status = 'CLOSED'` 的行，用于台账历史过滤与「重新评估建单」的前置判断：已关闭订单不参与可操作订单集合。关闭原因记录在 `close_reason`。

## 需求背景

批量白名单、到期处理与人工关闭都会产生关闭态订单（见 [[batch_whitelist_defer]]、[[renewal_remind_expire]]），需要一个统一口径将其排除在活跃订单之外。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 订单已关闭口径
predicate: ca_fee_order.order_status = 'CLOSED'
scope: 台账历史过滤、重新评估建单
evidence: CaFeeLedgerQueryService.java
```