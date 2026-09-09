---
type: caliber
title: 延期支付企业
page_key: defer_pay_company
belong: calibers
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

延期支付企业口径用于识别项目配置中存在 DEFER_PAY 配置且当前仍在延期服务期内的企业，这类企业可暂时豁免缴费。

## 需求背景

规则优先级链中需要在白名单之后、常规服务期判断之前识别延期支付企业，避免对仍在延期范围内的企业催缴。

## 版本演进

v0.1 草稿：来自 CaFeeRuleEngineService.resolveDeferPay 的代码证据，项目配置结构需进一步补充。

```ground:caliber
name: 延期支付企业
predicate: "项目配置special_company_list中存在config_type='DEFER_PAY'且today <= deferServiceEnd的企业"
scope: 企业+项目维度
evidence: code:CaFeeRuleEngineService.resolveDeferPay
```

相关：[[ca_fee_company]]、[[fee_rule_priority_chain]]