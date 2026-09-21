---
type: rule
title: 一证四步成功不是已缴费
page_key: four_step_not_fee
belong: rules
domain: ca_fee
status: draft
field_targets: [ca_certification_info.submit_status, ca_fee_order.order_status]
sources: ['code_path:CaCertificationController.java:88']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_certification_info, ca_fee_order]
---

# 一证四步成功不是已缴费

protocol/confirm 写 submit_status。预检失效回写企业 ca_register_status=N。都不改订单 order_status。

```ground:rule
rule: 一证四步成功不是已缴费
field_targets: [ca_certification_info.submit_status, ca_fee_order.order_status]
impact: write_constraint
content: protocol/confirm 写 submit_status。预检失效回写企业 ca_register_status=N。都不改订单 order_status。
evidence: code_path:CaCertificationController.java:88
```

## 页面链接

- [[tables/ca_certification_info]]
- [[tables/ca_fee_order]]
- [[dicts/ca_certification_info__submit_status]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_certification_info__submit_status]]
- [[processes/ca_fee_order__order_status]]
