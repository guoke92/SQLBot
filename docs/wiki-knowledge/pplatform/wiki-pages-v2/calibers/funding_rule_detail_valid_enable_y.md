---
type: caliber
title: 资方规则详情-有效口径
page_key: calibers/funding_rule_detail_valid_enable_y
domain: funding
status: draft
aliases:
  - 规则详情有效口径
  - rule_detail enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyRuleProviderImpl#doQuery"
  - "code:FundRuleInfoApplication#getRuleInfoById"
  - "db:funding_rule_detail"
contract_version: "0.1"
---

# 资方规则详情-有效口径

## 业务定位

明细的读取一律带 `enable = 'Y'`：无论是对外查询组装规则包，还是运营侧按 id 查看规则详情，都只取有效明细行。保存侧同样以 `enable='Y'` 作为幂等匹配条件（命中即更新、否则新增），因此「失效一条旧明细、新增一条同 `rule_key` 明细」在有 `enable` 过滤的前提下不会互相污染。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:caliber
caliber: 资方规则详情-有效
predicate: "funding_rule_detail.enable = 'Y'"
scope: 规则详情/对外查询
evidence: "code:FundingPartyRuleProviderImpl#doQuery; FundRuleInfoApplication#getRuleInfoById"
```

## 关联

- 表：[[tables/funding_rule_detail]]
- 规则：[[rules/rule_detail_save_idempotent]]