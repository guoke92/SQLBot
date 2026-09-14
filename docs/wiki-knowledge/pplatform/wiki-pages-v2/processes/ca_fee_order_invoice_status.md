---
type: process
title: 发票状态机
page_key: ca_fee_order_invoice_status
domain: CA证书收费
status: draft
aliases:
  - 发票状态
  - invoice_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: processes
---

发票状态机作用于 [[ca_fee_order]] 的 `invoice_status`，与缴费主流程**异步**：缴费成功后由 `CaFeeInvoiceApplication.requestInvoiceAsync` 将 `invoice_status` 置为 `PENDING`，已存在非 `NONE` 状态则跳过，见 [[invoice_async]]、[[invoice_status_pending]]。

`NONE` 表示无需开票（初始态），`PENDING` 开票中，`ISSUED` 已开票，`FAILED` 开票失败。开票失败后的重试路径在当前证据中未给出。

## 需求背景

开票不阻塞缴费主流程：缴费成功页仅提示「开票中」，开票动作由异步任务承担，因此发票状态与订单状态可以短暂不一致。

## 版本演进

- v0（本页）：依据语义分析建立首版状态机；`FAILED` 之后的恢复路径待补。

```ground:process
name: 发票状态
field: ca_fee_order.invoice_status
states:
  - value: NONE
    label: 无需开票
    source: code_enum
  - value: PENDING
    label: 开票中
    source: code_enum
  - value: ISSUED
    label: 已开票
    source: code_enum
  - value: FAILED
    label: 开票失败
    source: code_enum
transitions:
  - from: NONE
    event: 缴费成功后异步申请开票
    to: PENDING
    evidence: code_path:CaFeeInvoiceApplication.java:49
```