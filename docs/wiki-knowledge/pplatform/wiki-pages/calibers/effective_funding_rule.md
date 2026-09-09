---
type: caliber
title: 生效资方规则
page_key: effective_funding_rule
belong: calibers
domain: 资金方规则与异常解决
status: published
aliases:
  - 生效规则
oid: 1

sources:
  - code:FundingPartyRuleProviderImpl.doQuery
contract_version: "0.1"
field_targets: [funding_rule_info.rule_status]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径定义了 [[funding_rule_info]] 中生效规则的判定标准：rule_status 必须等于 'ACTIVE'。该口径应用于对外规则查询（Dubbo Provider），确保只有生效的规则才会被下游调用方获取。

## 需求背景

规则具有生命周期，只有 ACTIVE 状态的规则才能对外提供。该口径与 [[funding_rule_info_rule_status]] 状态机中的 ACTIVE 状态直接对应。

## 版本演进

本口径当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:caliber
name: "生效资方规则"
predicate: "funding_rule_info.rule_status = 'ACTIVE'"
scope: "对外规则查询（Dubbo Provider）"
evidence: "code:FundingPartyRuleProviderImpl.doQuery"
```