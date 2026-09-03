---
type: caliber
title: 有效规则详情
page_key: effective_rule_detail
domain: 资金方规则与异常解决
status: published
aliases:
  - 有效明细记录
oid: 1

sources:
  - code:FundRuleInfoApplication.getRuleInfoById
  - code:FundingPartyRuleProviderImpl.doQuery
contract_version: "0.1"
field_targets: [funding_rule_detail.enable]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径定义了 [[funding_rule_detail]] 中有效明细记录的判定标准：enable 必须等于 'Y'。该口径应用于查询规则详情和组装规则的场景。

## 需求背景

规则明细同样支持软删除。查询规则详情时只需返回有效明细，组装规则时也只需包含 enable='Y' 的明细。

## 版本演进

本口径当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:caliber
name: "有效规则详情"
predicate: "funding_rule_detail.enable = 'Y'"
scope: "查询规则详情、组装规则"
evidence: "code:FundRuleInfoApplication.getRuleInfoById / FundingPartyRuleProviderImpl.doQuery"
```