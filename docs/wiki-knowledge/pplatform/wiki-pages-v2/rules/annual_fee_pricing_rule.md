---
type: rule
title: 年费定价规则
page_key: rules/annual_fee_pricing_rule
domain: CA证书收费
status: draft
aliases: [resolveAnnualFee, 应缴年费取值规则]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeeRuleEngineService.java:resolveAnnualFee
contract_version: "0.1"
---

# 年费定价规则

## 业务定位

应缴年费按**优先级**解析：① 生效中的特殊年费（`special_annual_fee`）→ ② 已锁定的年费（`locked_annual_fee`）→ ③ 项目角色价（`core_annual_fee` / `supplier_annual_fee`）。结果落在订单 `annual_fee`。

业务含义：**特殊配置优先于历史锁定价，历史锁定价优先于项目当前标准价**。因此项目调价不会影响已锁定企业，而特殊配置企业则以特殊价为准（豁免情形见[[calibers/whitelist_exempt]]，减免情形见[[calibers/targeted_reduction]]）。字段来源：[[tables/ca_fee_company]]、[[tables/ca_fee_project_config]]；落点[[tables/ca_fee_order]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

决定订单 annual_fee。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 年费定价规则
content: 应缴年费按优先级：生效中的特殊年费（special_annual_fee）→ 已锁定的年费（locked_annual_fee）→ 项目角色价（core_annual_fee / supplier_annual_fee）。
impact: 决定订单 annual_fee。
field_targets: [ca_fee_company.special_annual_fee, ca_fee_company.locked_annual_fee, ca_fee_project_config.core_annual_fee, ca_fee_project_config.supplier_annual_fee]
evidence: "code_path:CaFeeRuleEngineService.java:resolveAnnualFee"
```