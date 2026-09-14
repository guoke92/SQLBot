---
type: caliber
title: 订单已缴费口径
page_key: order_status_paid
domain: CA证书收费
status: draft
aliases:
  - 已缴订单
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeOrderApplication.java
contract_version: "0.1"
belong: calibers
---

订单已缴费口径指 [[ca_fee_order]] 中 `order_status = 'PAID'` 的行，用于缴费成功判定、台账展示与编辑限制（已缴费订单不允许改回未缴费，见 [[ledger_edit_limit]]）。服务期内已缴费豁免亦会以「存在 PAID 且服务期覆盖今天的订单」为条件，见 [[already_paid_in_service]]。

## 需求背景

订单级已缴费是金额与协议快照的最终确认态，与 [[company_pay_status_paid]] 的企业级汇总状态分工明确。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 订单已缴费口径
predicate: ca_fee_order.order_status = 'PAID'
scope: 缴费成功、台账展示、编辑限制
evidence: CaFeeOrderApplication.java
```