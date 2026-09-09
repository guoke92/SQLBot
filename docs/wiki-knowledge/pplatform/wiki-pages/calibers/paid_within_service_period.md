---
type: caliber
title: 服务期内已缴费
page_key: paid_within_service_period
belong: calibers
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.service_end]
scope:
  databases: [lowcode_pplatform]
---

服务期内已缴费口径用于识别当前仍在服务有效期内且已缴费的企业，避免重复缴费或到期前催缴。

## 需求背景

规则评估中该口径作为收费判断的重要分支，若企业满足服务期内已缴费，则不进入需缴费分支。

## 版本演进

v0.1 草稿：来自 CaFeeRuleEngineService 场景四的代码证据，需进一步确认场景编号与实现映射。

```ground:caliber
name: 服务期内已缴费
predicate: "ca_fee_company.service_end >= today OR 存在PAID订单且service_end >= today"
scope: 企业维度
evidence: code:CaFeeRuleEngineService场景四
```

相关：[[ca_fee_company]]、[[ca_fee_order]]、[[fee_rule_priority_chain]]