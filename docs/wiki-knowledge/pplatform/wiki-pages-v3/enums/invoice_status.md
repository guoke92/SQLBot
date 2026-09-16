---
type: enum
title: invoice_status
page_key: invoice_status
domain: CA证书收费
status: draft
aliases: [开票状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeInvoiceStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# invoice_status

[[ca_fee_order]] 的 `invoice_status`。`CaFeeInvoiceStatusEnum`。

```ground:enum
enum: invoice_status
fields: [ca_fee_order.invoice_status]
values:
  "PENDING":
    label: "开票中"
  "ISSUED":
    label: "已开票"
  "FAILED":
    label: "开票失败"
  "NONE":
    label: "无需开票"
```
