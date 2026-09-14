---
type: process
title: CA服务费订单状态机
page_key: ca_fee_order_state
domain: CA证书收费
status: draft
aliases: [订单状态流转, order_status 状态机, CA订单状态]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
  - code:CaFeePaymentApplication.java
  - code:CaFeeOrderApplication.java
  - code:CaFeeLedgerOperateService.java
  - code:CaFeeRenewalService.java
contract_version: "0.1"
belong: processes
---

# CA服务费订单状态机

## 业务定位

本页描述[[tables/ca_fee_order]]中 `order_status` 的生命周期。订单从 `PENDING`（未缴费）出发，仅有四条已证实出口：**缴费成功转 `PAID`**；**手动/系统关闭、批量加白名单、服务到期处理**三条路径转入 `CLOSED`。

`PAID` 之后的状态变更（如发票、退费）在本次语义分析中**没有代码证据**，不在本页断言。此外，库中实际存在 `PAIDING`、`UNPAID` 两个代码枚举未声明的值，说明存在其他写入路径或历史数据，需以口径页而非枚举全集来统计。

支付成功的前置条件（`PENDING` + `agreement_signed='Y'`）见[[rules/payment_precondition_rule]]，协议签署自身的状态机见[[processes/ca_fee_agreement_sign]]，服务到期关闭 RENEW 待缴单的时点背景见[[rules/renew_remind_rule]]。待支付、已支付两个统计口径见[[calibers/pending_order]]与[[calibers/paid_order]]。

## 需求背景

本页为代码侧状态流转的事实归档，本次语义分析未提供需求文档主张（reqdoc 锚点）。"批量加白名单"与"服务到期"两条进入 `CLOSED` 的路径属于系统动作，与人工关闭在业务语义上不同，但均落在同一终态。

## 版本演进

- 本次语义分析未提供与本状态机相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:state_machine
name: CA服务费订单状态机
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
  - value: PAIDING
    label: 支付中（DB实际存在，代码未声明）
    source: db_dist
  - value: UNPAID
    label: 未缴费（DB实际存在，代码未声明）
    source: db_dist
transitions:
  - from: PENDING
    event: 缴费成功 markPaid
    to: PAID
    evidence: "code_path:CaFeePaymentApplication.java:handlePaySuccess"
  - from: PENDING
    event: 手动/系统关闭订单 closeOrder
    to: CLOSED
    evidence: "code_path:CaFeeOrderApplication.java:closeOrder"
  - from: PENDING
    event: 批量加白名单
    to: CLOSED
    evidence: "code_path:CaFeeLedgerOperateService.java:applyWhitelist"
  - from: PENDING
    event: 服务到期处理关闭RENEW待缴单
    to: CLOSED
    evidence: "code_path:CaFeeRenewalService.java:processServiceExpired"
```