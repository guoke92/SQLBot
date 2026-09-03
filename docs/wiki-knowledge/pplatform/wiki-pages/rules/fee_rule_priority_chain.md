---
type: rule
title: 收费规则优先级链
page_key: fee_rule_priority_chain
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.pay_status, ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

收费规则优先级链是 CA 服务费规则评估的核心判定顺序。它按项目未开启收费、白名单、延期支付、服务期内已缴费、年费为 0、需缴费的顺序依次判断，决定企业是否需要缴费及费用状态。

## 需求背景

业务上存在多种豁免或已缴费场景，必须以固定优先级进行判断，避免同一企业被多个规则重复定性。

## 版本演进

v0.1 草稿：来自 CaFeeRuleEngineService.evaluate 的代码证据，后续可补充边界条件与返回结构。

```ground:rule
name: 收费规则优先级链
content: "按顺序判定：1)项目未开启收费→EXEMPT/PROJECT_DISABLED；2)白名单→EXEMPT/WHITELIST；3)延期支付→EXEMPT/DEFER_PAY；4)服务期内已缴费→PAID/ALREADY_PAID；5)年费为0→EXEMPT/WHITELIST；6)需缴费→UNPAID/EXPIRED，needPay=true"
impact: "决定企业是否需要缴费及费用状态"
field_targets:
  - ca_fee_company.pay_status
  - ca_fee_order.order_status
evidence: code_path:CaFeeRuleEngineService.evaluate
```

相关：[[unpaid_company]]、[[whitelist_exempt_company]]、[[defer_pay_company]]、[[paid_within_service_period]]

相关：[[ca_fee_company]] [[ca_fee_order]]
