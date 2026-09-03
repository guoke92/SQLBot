---
type: caliber
title: 有效前端配置
page_key: effective_front_cfg
domain: 资金方规则与异常解决
status: published
aliases:
  - 有效前端字段配置
oid: 1

sources:
  - code:FundRuleInfoApplication.validateRuleLayerAndFrontCfg
  - code:FundingPartyRuleProviderImpl.doQuery
contract_version: "0.1"
field_targets: [funding_rule_front_cfg.enable]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径定义了 [[funding_rule_front_cfg]] 中有效前端配置的判定标准：enable 必须等于 'Y'。该口径应用于导入校验和规则查询场景。

## 需求背景

前端配置用于定义规则的可配置项和校验规则。导入和查询时都需要过滤有效配置，确保使用的是当前启用的前端配置。

## 版本演进

本口径当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:caliber
name: "有效前端配置"
predicate: "funding_rule_front_cfg.enable = 'Y'"
scope: "导入校验、规则查询"
evidence: "code:FundRuleInfoApplication.validateRuleLayerAndFrontCfg / FundingPartyRuleProviderImpl.doQuery"
```