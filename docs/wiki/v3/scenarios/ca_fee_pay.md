---
type: scenario
title: 缴纳 CA 服务费
page_key: ca_fee_pay
belong: scenarios
domain: ca_fee
status: draft
aliases: [CA收费, 电子签章服务费]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order, ca_fee_company, ca_fee_project_config]
---

# 缴纳 CA 服务费

项目开启收费后按统码建 PENDING 订单，交e保支付后订单 PAID、企业宽表写服务周期。
问「是否已缴费」用 covering_paid_ca_fee_order / in_period_ca_fee_company，不要只看 pay_status。


```ground:scenario
scenario: ca_fee_pay
hubs:
- table: ca_fee_order
  role: master
shared:
- table: ca_fee_company
  role: ledger
- table: ca_fee_project_config
  role: project_charge
lifecycle:
- dict: ca_fee_order__order_status
  process: ca_fee_order__order_status
- dict: ca_fee_company__pay_status
  process: ca_fee_company__pay_status
```

## 页面链接

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[tables/ca_fee_project_config]]
- [[dicts/ca_fee_company__pay_status]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_fee_company__pay_status]]
- [[processes/ca_fee_order__order_status]]
