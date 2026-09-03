---
type: rule
title: 收费规则引擎豁免链
page_key: rule_engine_exemption_chain
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.pay_status, ca_fee_order.annual_fee, ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

# 收费规则引擎豁免链

业务定位：定义收费评估的优先级顺序，首个命中的豁免条件即决定最终是否需要缴费。

## 需求背景

规则引擎按顺序检查：项目未开启收费 → 白名单(0元) → 延期支付 → 服务期内已缴费 → 定价为0 → 需缴费。该链避免重复计算，提升评估效率。

## 版本演进

当前链固定，未来可能增加新的豁免条件或支持配置化。

```ground:rule
name: 收费规则引擎豁免链
content: 项目未开启收费→白名单(0元)→延期支付→服务期内已缴费→定价为0→需缴费；首个命中即返回
impact: 决定是否需要缴费及费用状态
field_targets: ["ca_fee_company.pay_status", "ca_fee_order.order_status", "ca_fee_order.annual_fee"]
evidence: code:CaFeeRuleEngineService.evaluate
```

[[paid_order]] · [[multi_project_pass]] · [[ca_fee_company]] · [[ca_fee_order]]