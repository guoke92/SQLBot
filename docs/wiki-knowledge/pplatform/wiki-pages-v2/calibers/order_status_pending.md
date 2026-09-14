---
type: caliber
title: 订单未缴费口径
page_key: order_status_pending
domain: CA证书收费
status: draft
aliases:
  - 待缴订单
  - PENDING
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeOrderApplication.java
contract_version: "0.1"
belong: calibers
---

订单未缴费口径指 [[ca_fee_order]] 中 `order_status = 'PENDING'` 的行，界定协议签署、支付、关闭订单的**可操作范围**。台账编辑同样只在此状态（与 `PAID`）下开放，见 [[ledger_edit_limit]]。

## 需求背景

支付与签署动作必须以订单为闸门，避免在企业级汇总状态上做状态迁移，从而保证一笔订单一次缴费的可追溯性。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 订单未缴费口径
predicate: ca_fee_order.order_status = 'PENDING'
scope: 协议签署、支付、关闭订单可操作范围
evidence: CaFeeOrderApplication.java
```