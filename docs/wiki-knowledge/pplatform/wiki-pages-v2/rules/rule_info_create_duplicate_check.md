---
type: rule
title: 资方规则-新增查重
page_key: rules/rule_info_create_duplicate_check
domain: funding
status: draft
aliases:
  - 资方规则重复新增校验
  - 不允许重复新增
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
---

# 资方规则-新增查重

## 业务定位

当 `ruleInfoId` 为空（即新增）时，按 `productCode + fundingPartyMark` 查重，已存在则抛「不允许重复新增」。这确立了「**同一产品下同一资方只有一条规则主记录**」的模型——后续修改必须走更新路径（`ruleInfoId` 非空）以累加版本，而不是新建第二条。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该查重与 [[rules/rule_info_update_version_increment]] 的版本累加共同构成「一资方一规则、版本留痕」的设计。

```ground:rule
rule: 资方规则-新增查重
content: "ruleInfoId 为空时按 productCode + fundingPartyMark 查重，已存在则抛「不允许重复新增」"
impact: "同产品下同一资方唯一规则"
field_targets:
  - funding_rule_info.product_code
  - funding_rule_info.funding_party_mark
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 规则：[[rules/rule_info_update_version_increment]]、[[rules/rule_info_create_initial_pending]]