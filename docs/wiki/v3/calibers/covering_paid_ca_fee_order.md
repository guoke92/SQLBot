---
type: caliber
title: 覆盖当日的已缴 CA 服务费订单
page_key: covering_paid_ca_fee_order
belong: calibers
domain: ca_fee
status: draft
field_targets: [ca_fee_order.order_status, ca_fee_order.enable, ca_fee_order.service_end]
sources: ['code_path:cafee/CaFeeOrderService.java:119']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_order, ca_fee_company]
---

# 覆盖当日的已缴 CA 服务费订单

回答「这笔统码当前服务期是否已缴费」。规则引擎场景四：企业宽表 service_end≥today，否则用本口径兜底。
不要只用 ca_fee_company.pay_status=PAID（到期任务会把宽表写成 UNPAID）。


```ground:caliber
caliber: 覆盖当日的已缴 CA 服务费订单
field_targets: [ca_fee_order.order_status, ca_fee_order.enable, ca_fee_order.service_end]
predicate: ca_fee_order.order_status = 'PAID' AND ca_fee_order.enable = 'Y' AND ca_fee_order.service_end
  >= CURRENT_DATE
scope: global
boundary: '回答「这笔统码当前服务期是否已缴费」。规则引擎场景四：企业宽表 service_end≥today，否则用本口径兜底。

  不要只用 ca_fee_company.pay_status=PAID（到期任务会把宽表写成 UNPAID）。

  '
using_relations:
- left: ca_fee_company.certification_no
  right: ca_fee_order.certification_no
evidence: code_path:cafee/CaFeeOrderService.java:119
```

## 页面链接

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[dicts/ca_fee_order__enable]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_fee_order__order_status]]
