---
type: process
title: CA服务费订单状态
page_key: ca_fee_order__order_status
belong: processes
domain: ca_fee
status: draft
anchors: [ca_fee_order.order_status]
field_targets: [ca_fee_order.order_status]
sources: ['code_path:cafee/CaFeeOrderService.java:486', 'code_path:cafee/CaFeeOrderService.java:426',
  'code_path:cafee/CaFeeOrderService.java:312']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_order, ca_fee_company]
---

# CA服务费订单状态

钉 ca_fee_order.order_status。建单 PENDING；支付写 PAID 并同步企业宽表；关闭写 CLOSED。
枚举有 EXPIRED，现网未见 setOrderStatus(EXPIRED)。不要把企业 pay_status 或规则引擎 feeStatus 当成订单状态。


```ground:process
process: CA服务费订单状态
field: ca_fee_order.order_status
entry: POST /cust-web/caFee
stages:
- stage: 建单
  transitions:
  - from: PENDING
    event: doCreateOrGetPendingOrderDetail
    to: PENDING
    evidence: code_path:cafee/CaFeeOrderService.java:486
- stage: 支付
  transitions:
  - from: PENDING
    event: markPaid
    to: PAID
    evidence: code_path:cafee/CaFeeOrderService.java:426
  effects:
  - op: syncCompanyAfterPaid 置为 PAID 并写服务周期
    table: ca_fee_company
    fields: [pay_status]
- stage: 关闭
  transitions:
  - from: PENDING
    event: closeOrder
    to: CLOSED
    evidence: code_path:cafee/CaFeeOrderService.java:312
```

## 页面链接

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[dicts/ca_fee_order__order_status]]
