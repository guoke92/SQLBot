---
type: caliber
title: 前端规则配置-有效口径
page_key: calibers/funding_rule_front_cfg_valid_enable_y
domain: funding
status: draft
aliases:
  - 前端配置有效口径
  - front_cfg enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg"
  - "code:FundingPartyRuleProviderImpl#doQuery"
  - "db:funding_rule_front_cfg"
contract_version: "0.1"
---

# 前端规则配置-有效口径

## 业务定位

[[tables/funding_rule_front_cfg]] 的读取统一带 `enable = 'Y'`：页面按 `rule_layer` 分组渲染配置项、导入时按 `product + rule_layer + key_name` 匹配前端字段、对外查询组装规则包，三处都只认有效配置。这意味着下线一个字段的规范做法是把配置置为非 `Y`，而不是删行——历史明细中的 `rule_key` 仍可追溯。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:caliber
caliber: 前端规则配置-有效
predicate: "funding_rule_front_cfg.enable = 'Y'"
scope: 页面配置/导入匹配/对外查询
evidence: "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg; FundingPartyRuleProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_rule_front_cfg]]
- 概念：[[concepts/rule_key]]、[[concepts/rule_layer]]