---
type: rule
title: 发票异步规则
page_key: invoice_async
domain: CA证书收费
status: draft
aliases:
  - requestInvoiceAsync
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeInvoiceApplication.java
contract_version: "0.1"
belong: rules
---

缴费成功后异步 `requestInvoiceAsync`：先将订单 `invoice_status` 置 `PENDING`，已存在非 `NONE` 状态则跳过。相关口径见 [[invoice_status_pending]]，状态机见 [[ca_fee_order_invoice_status]]。

## 需求背景

开票链路涉及外部系统，若同步执行会阻塞缴费主流程；因此异步化并以状态判断做幂等，保证同一订单不重复申请开票。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 发票异步规则
content: 缴费成功后异步 requestInvoiceAsync，先将订单 invoice_status 置 PENDING，已存在非 NONE 状态则跳过
impact: 开票不阻塞缴费主流程
field_targets:
  - ca_fee_order.invoice_status
evidence: CaFeeInvoiceApplication.requestInvoiceAsync
```