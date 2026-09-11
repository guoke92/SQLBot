---
type: enum
title: invoice_status
page_key: invoice_status
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# invoice_status

（权威枚举页：4 值，绑定方式 setter-evidence，主承载 ca_fee_order.invoice_status；db 实测分布。）

```ground:enum
enum: invoice_status
fields: [ca_fee_order.invoice_status]
values:
  PENDING:
    label: 开票中
  ISSUED:
    label: 已开票
  FAILED:
    label: 开票失败
  NONE:
    label: 无需开票
```
