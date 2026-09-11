---
type: rule
title: 资方规则-对外仅返回ACTIVE
page_key: rules/rule_info_provider_active_only
domain: funding
status: draft
aliases:
  - 对外只返回生效规则
  - Dubbo 仅 ACTIVE
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---

# 资方规则-对外仅返回ACTIVE

## 业务定位

Dubbo 查询按 `fundingPartyMark + productCode + rule_status='ACTIVE'` 取规则，取不到则**返回 null**（而非空对象或异常）。这是内外可见性的分界线：外部系统只能消费已生效规则，`PENDING` 与 `INACTIVE` 对外均不可见。对应口径 [[calibers/funding_rule_info_active_rule]]。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。返回 null 的约定要求调用方必须做空值判断。

```ground:rule
rule: 资方规则-对外仅返回ACTIVE
content: "Dubbo 查询按 fundingPartyMark + productCode + rule_status=ACTIVE 取规则，否则返回 null"
impact: "外部只能消费已生效规则"
field_targets:
  - funding_rule_info.rule_status
evidence: "code:FundingPartyRuleProviderImpl#doQuery"
```

## 关联

- 口径：[[calibers/funding_rule_info_active_rule]]、[[calibers/funding_rule_detail_valid_enable_y]]
- 流程：[[processes/funding_rule_status_machine]]