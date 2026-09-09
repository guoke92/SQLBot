---
type: caliber
title: 白名单豁免企业
page_key: whitelist_exempt_company
belong: calibers
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.special_annual_fee, ca_fee_company.special_config_flag]
scope:
  databases: [lowcode_pplatform]
---

白名单豁免企业口径用于识别通过特殊配置实现年费为 0 的豁免企业。

## 需求背景

规则评估中需要在项目收费开启后优先识别白名单企业，使其免于生成正常缴费要求，并可能触发旧订单清理。

## 版本演进

v0.1 草稿：来自 CaFeeRuleEngineService.isWhitelistExempt 的代码证据。

```ground:caliber
name: 白名单豁免企业
predicate: "ca_fee_company.special_config_flag = 'Y' AND ca_fee_company.special_annual_fee = 0"
scope: 企业维度
evidence: code:CaFeeRuleEngineService.isWhitelistExempt
```

相关：[[ca_fee_company]]、[[fee_rule_priority_chain]]、[[whitelist_batch_operation]]