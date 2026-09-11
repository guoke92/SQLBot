---
type: concept
title: 规则层（ruleLayer）
page_key: concepts/rule_layer
domain: funding
status: draft
aliases:
  - ruleLayer
  - rule_layer
  - 规则层
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:RuleLayerEnum"
  - "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg"
contract_version: "0.1"
maps_to: "UNDERLYING / FINANCING / OTHER（RuleLayerEnum）"
field_targets:
  - funding_rule_detail.rule_layer
  - funding_rule_front_cfg.rule_layer
adjudication: boundary
also_confused_with:
  - 规则层级显示名(底层规则/融资规则/其他规则)
boundary: "导入模板填显示名，经 RuleLayerEnum.getDisplayName 反查 dictKey；存储与查询使用 dictKey"
---

# 规则层（ruleLayer）

## 业务定位

规则层是资方规则的**分组维度**，枚举为 `UNDERLYING`（底层）/ `FINANCING`（融资）/ `OTHER`（其他）。页面配置（[[tables/funding_rule_front_cfg]]）按此分组渲染，规则明细（[[tables/funding_rule_detail]]）按此归类；保存前还有专门的 `validateRuleLayerAndFrontCfg` 校验规则层与前端配置是否自洽。

**边界**：导入模板里运营填的是**显示名**（「底层规则 / 融资规则 / 其他规则」），系统经 `RuleLayerEnum.getDisplayName` 反查得到 `dictKey`；存储与查询一律使用 `dictKey`。导入时的字段匹配用三元组 `product + rule_layer + key_name`，此处的 `rule_layer` 同样是 `dictKey`。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/rule_key]]
- 表：[[tables/funding_rule_front_cfg]]、[[tables/funding_rule_detail]]