---
type: rule
title: 白名单批量操作
page_key: whitelist_batch_operation
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.special_annual_fee, ca_fee_company.special_config_flag, ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

白名单批量操作规则在批量加入白名单时，若企业存在 PENDING 订单则关闭该订单，并创建 0 元年费订单完成流程。

## 需求背景

白名单生效后需要清理旧的待支付订单，避免继续催缴，并以 0 元年费订单完成流程闭环。

## 版本演进

v0.1 草稿：来自 CaFeeLedgerOperateService.applyWhitelist 的代码证据。

```ground:rule
name: 白名单批量操作
content: "批量加白名单时，若存在PENDING订单则关闭该订单，并创建0元年费订单完成流程"
impact: "白名单生效后清理旧订单"
field_targets:
  - ca_fee_order.order_status
  - ca_fee_company.special_config_flag
  - ca_fee_company.special_annual_fee
evidence: code_path:CaFeeLedgerOperateService.applyWhitelist
```

相关：[[whitelist_exempt_company]]、[[ca_fee_order]]、[[ca_fee_company]]