---
type: rule
title: 批量白名单操作
page_key: batch_whitelist
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.special_config_flag, ca_fee_order.annual_fee, ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

# 批量白名单操作

业务定位：支持批量设置企业为白名单，豁免缴费并生成 0 元订单记录。

## 需求背景

部分企业符合减免条件，需通过白名单机制快速处理。该规则保存特殊配置，创建 0 元订单，并关闭当前待支付订单，保证数据一致性。

## 版本演进

当前批量操作基于代码实现，未来可能支持更灵活的豁免规则配置。

```ground:rule
name: 批量白名单操作
content: 保存白名单特殊配置，创建0元订单，关闭当前 PENDING 订单
impact: 豁免缴费并生成0元订单记录
field_targets: ["ca_fee_order.order_status", "ca_fee_order.annual_fee", "ca_fee_company.special_config_flag"]
evidence: code:CaFeeLedgerOperateService.batchWhitelist
```

[[ca_fee_company]] · [[ca_fee_order]] · [[rule_engine_exemption_chain]]