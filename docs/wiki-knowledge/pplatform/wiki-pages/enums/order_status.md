---
type: enum
title: order_status
page_key: order_status
belong: enums
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# order_status

（权威枚举页：4 值，绑定方式 setter-evidence，主承载 ca_fee_order.order_status；db 实测分布，基线外 2 值。）

```ground:enum
enum: order_status
fields: [ca_fee_order.order_status]
values:
  PENDING:
    label: 未缴费
  PAID:
    label: 已缴费
  CLOSED:
    label: 已关闭
  EXPIRED:
    label: 已过期
  PAIDING:
    label: "PAIDING"
    note: db 分布存在但代码枚举未声明（REVIEW）
  UNPAID:
    label: "UNPAID"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
