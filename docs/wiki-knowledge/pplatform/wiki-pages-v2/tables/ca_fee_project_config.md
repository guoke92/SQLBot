---
type: table
title: ca_fee_project_config CA收费项目配置表
page_key: tables/ca_fee_project_config
domain: CA证书收费
status: draft
aliases: [CA收费项目配置, 项目收费开关配置, ca_fee_project_config]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_project_config
  - code:CaFeeRuleEngineService.java
  - code:CaFeePaymentCheckApplication.java
contract_version: "0.1"
---

# ca_fee_project_config CA收费项目配置表

## 业务定位

`ca_fee_project_config` 是 CA 证书收费的**项目级策略表**：它决定某个项目是否开启 CA 收费（`charge_enabled`）、核企与供应商各自的年费标准（`core_annual_fee` / `supplier_annual_fee`）、特殊企业名单（白名单、定向减免、延期支付），以及**哪些业务场景需要拦截**（`block_scene_list`）。

这张表是[[rules/rule_engine_priority|规则引擎优先级]]的第一道判断：项目未开启收费即整体放行；也是[[rules/intercept_scene_rule|拦截场景规则]]的唯一字段来源——即便判定需缴费，只有当前请求场景命中 `block_scene_list` 才会真正阻断业务节点。年费取值优先级见[[rules/annual_fee_pricing_rule]]，与[[tables/ca_fee_company]]中的特殊/锁定年费共同决定订单 `annual_fee`。

## 需求背景

本页字段语义来自库表与代码两侧证据，本次语义分析未提供需求文档主张（reqdoc 锚点）。"特殊企业配置"如何落到企业维度快照（`special_config_flag` / `special_annual_fee`）见[[rules/multi_project_exemption_rule]]与企业表[[tables/ca_fee_company]]。

## 版本演进

- 本次语义分析未提供与本表相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:columns
table: ca_fee_project_config
columns:
  - field: charge_enabled
    meaning: 项目是否开启 CA 收费：Y/N
    evidence: code
  - field: core_annual_fee
    meaning: 核心企业年费（元）
    evidence: code
  - field: supplier_annual_fee
    meaning: 供应商年费（元）
    evidence: code
  - field: special_company_list
    meaning: 特殊企业配置 JSON 列表（白名单/定向减免/延期支付）
    evidence: code
  - field: block_scene_list
    meaning: 收费拦截场景列表
    evidence: code
```

相关口径：[[calibers/charge_enabled_project]]；相关规则：[[rules/intercept_scene_rule]]、[[rules/annual_fee_pricing_rule]]、[[rules/rule_engine_priority]]。