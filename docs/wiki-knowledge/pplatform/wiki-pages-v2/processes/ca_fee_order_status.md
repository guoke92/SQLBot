---
type: process
title: CA服务费订单状态机
page_key: ca_fee_order_status
domain: CA证书收费
status: draft
aliases:
  - 订单状态
  - order_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: processes
---

订单状态机作用于 [[ca_fee_order]] 的 `order_status`，是支付、关闭、台账展示与重新评估建单的共同支点。`PENDING` 是唯一可支付、可签署协议、可人工关闭的状态（口径 [[order_status_pending]]）；`PAID` 表示缴费完成（口径 [[order_status_paid]]）；`CLOSED` 表示订单终止（口径 [[order_status_closed]]）；`EXPIRED` 枚举存在但**未使用**。

进入 `PAID` 的路径是「订单维度支付成功」，同时会回写企业维度 `pay_status`（见 [[ca_fee_company_pay_status]]、[[paid_payment]]）；进入 `CLOSED` 的路径有三类：人工关闭、批量白名单命中时关闭待缴单（见 [[batch_whitelist_defer]]）、以及到期处理流程中的关闭（见 [[renewal_remind_expire]]）。

## 需求背景

订单状态既是操作闸门也是统计口径：待缴费口径用于筛选可操作订单，已缴费口径用于台账展示与编辑限制（[[ledger_edit_limit]]），已关闭口径用于台账历史过滤与重新评估建单。

## 版本演进

- v0（本页）：依据语义分析中的状态与迁移证据建立首版状态机；`EXPIRED` 保留为已定义未使用状态。

```ground:process
name: CA服务费订单状态
field: ca_fee_order.order_status
states:
  - value: PENDING
    label: 未缴费
    source: code_enum
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: CLOSED
    label: 已关闭
    source: code_enum
  - value: EXPIRED
    label: 已过期
    source: code_enum
transitions:
  - from: PENDING
    event: 支付成功 markPaid
    to: PAID
    evidence: code_path:CaFeeOrderService.java:279 + CaFeePaymentApplication.java
  - from: PENDING
    event: 关闭订单 closeOrder
    to: CLOSED
    evidence: code_path:CaFeeOrderApplication.java + CaFeeOrderService.java
  - from: PENDING
    event: 批量白名单命中并关闭待缴单
    to: CLOSED
    evidence: code_path:CaFeeLedgerOperateService.java
```