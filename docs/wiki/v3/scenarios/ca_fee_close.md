---
type: scenario
title: 关闭待缴 CA 订单
page_key: ca_fee_close
belong: scenarios
domain: ca_fee
status: draft
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order]
---

# 关闭待缴 CA 订单

关闭待缴 CA 订单

```ground:scenario
scenario: ca_fee_close
hubs:
- table: ca_fee_order
  role: master
lifecycle:
- dict: ca_fee_order__order_status
  process: ca_fee_order__order_status
```

## 页面链接

- [[tables/ca_fee_order]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_fee_order__order_status]]
