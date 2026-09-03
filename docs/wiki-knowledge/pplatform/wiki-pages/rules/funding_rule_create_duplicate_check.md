---
type: rule
title: 资方规则新增查重
page_key: funding_rule_create_duplicate_check
domain: 资金方规则与异常解决
status: published
aliases:
  - 规则新增查重
oid: 1

sources:
  - code:FundRuleInfoApplication.saveRuleInfo
contract_version: "0.1"
field_targets: [funding_rule_info.funding_party_mark, funding_rule_info.product_code]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则约束 [[funding_rule_info]] 表的新增行为。新增资金方规则时，先按 productCode + fundingPartyMark 查询 funding_rule_info；若已存在则抛出异常，不允许重复新增。

## 需求背景

同一产品下同一资金方只能有一条规则主记录。该规则保证 [[funding_rule_create_duplicate_check]] 的执行，其依据的 productCode 和 fundingPartyMark 与 [[funding_party_identifier]] 和 [[product_code]] 概念相关。

## 版本演进

本规则当前为 v0.1 初始契约版本，尚未记录任何未证实的主张。

```ground:rule
name: "资方规则新增查重"
content: "新增资金方规则时，先按 productCode + fundingPartyMark 查询 funding_rule_info；若已存在则抛出异常，不允许重复新增。"
impact: "保证同一产品下同一资方只有一条规则主记录。"
field_targets:
  - funding_rule_info.product_code
  - funding_rule_info.funding_party_mark
evidence: "code:FundRuleInfoApplication.saveRuleInfo 新增分支"
```