---
type: caliber
title: 发票开票中
page_key: invoice_status_pending
domain: CA证书收费
status: draft
aliases:
  - invoice_status = PENDING
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeInvoiceApplication.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_order]] 中 `invoice_status = 'PENDING'`，用于缴费成功页提示与异步开票前置判断：已处于非 `NONE` 状态时跳过重复申请，见 [[invoice_async]]、[[ca_fee_order_invoice_status]]。

## 需求背景

开票为异步动作，需要中间状态向用户表达「开票中」，同时作为幂等条件防止重复提交开票请求。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 发票开票中
predicate: ca_fee_order.invoice_status = 'PENDING'
scope: 缴费成功页提示、异步开票前置
evidence: CaFeeInvoiceApplication.java
```