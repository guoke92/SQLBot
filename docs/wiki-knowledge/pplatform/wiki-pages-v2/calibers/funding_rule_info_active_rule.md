---
type: caliber
title: 资方规则-生效规则口径
page_key: calibers/funding_rule_info_active_rule
domain: funding
status: draft
aliases:
  - 生效规则口径
  - rule_status=ACTIVE
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyRuleProviderImpl#doQuery"
  - "code:FundRuleInfoApplication#activeRule"
contract_version: "0.1"
---

# 资方规则-生效规则口径

## 业务定位

**对外**（Dubbo Provider）查询资方规则时，除 `fundingPartyMark + productCode` 之外必须叠加 `rule_status = 'ACTIVE'`，否则返回 null。这是「内外部可见性分离」的关键口径：运营侧可以查看并维护 `PENDING` / `INACTIVE` 规则，但外部系统永远只能消费已生效版本，从而保证规则变更不会半途泄露给上游。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该口径与状态机 [[processes/funding_rule_status_machine]] 的 `activeRule` 入口共同构成「生效即可见」的语义闭环。

```ground:caliber
caliber: 资方规则-生效规则
predicate: "funding_rule_info.rule_status = 'ACTIVE'"
scope: Dubbo 对外查询资金方规则
evidence: "code:FundingPartyRuleProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 流程：[[processes/funding_rule_status_machine]]
- 规则：[[rules/rule_info_provider_active_only]]