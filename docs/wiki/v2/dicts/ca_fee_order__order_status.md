---
type: dict
title: ca_fee_order.order_status
page_key: ca_fee_order__order_status
belong: dicts
status: draft
anchors: [ca_fee_order.order_status]
sources: ['database_profile:ca_fee_order.order_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [ca_fee_order]
---

# ca_fee_order.order_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `ca_fee_order.order_status`，表页 [[tables/ca_fee_order]]。

## 取值

```ground:dict
dict: ca_fee_order__order_status
fields: [ca_fee_order.order_status]
values:
  CLOSED: {trust: proposed}
  PENDING: {trust: proposed}
  PAID: {trust: proposed}
  PAIDING: {trust: proposed}
  UNPAID: {trust: proposed}
triage: keep
```
