---
type: concept
title: 规则键（ruleKey）
page_key: concepts/rule_key
domain: funding
status: draft
aliases:
  - ruleKey
  - rule_key
  - front_key
  - 规则键
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "db:funding_rule_front_cfg"
contract_version: "0.1"
maps_to: "funding_rule_front_cfg.front_key = funding_rule_detail.rule_key"
field_targets:
  - funding_rule_front_cfg.front_key
  - funding_rule_detail.rule_key
adjudication: boundary
also_confused_with:
  - key_name
  - front_key_name
boundary: "detail.rule_key 存 front_cfg.front_key（机器键）；key_name/front_key_name 为展示名，导入匹配用 key_name（product+rule_layer+key_name 三元组）"
sources: ["enrich:wiki-admin"]
---

# 规则键（ruleKey）

## 业务定位

「规则键」串起了资方规则的**定义侧**与**实例侧**：`funding_rule_front_cfg.front_key` 是机器键（定义），`funding_rule_detail.rule_key` 存的就是这个机器键（实例）。明细保存时的幂等粒度正是 `ruleInfoId + ruleKey + enable='Y'`。

**边界**：`key_name` / `front_key_name` 是**展示名**，不是键。导入模板中的「规则名称」列按 `key_name` 匹配，匹配条件为 `product + rule_layer + key_name` 三元组；也就是说，人读的是名称，机器认的是键。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/rule_layer]]
- 表：[[tables/funding_rule_front_cfg]]、[[tables/funding_rule_detail]]
- 规则：[[rules/rule_detail_save_idempotent]]

相关：[[funding_rule_detail]] [[funding_rule_front_cfg]]
