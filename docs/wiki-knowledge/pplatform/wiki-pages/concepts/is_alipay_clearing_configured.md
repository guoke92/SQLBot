---
type: concept
title: 支付宝清分配置标识
page_key: concept/is_alipay_clearing_configured
domain: 支付宝蚂蚁档案与清算
status: published
aliases: ["configured", "isAlipayClearingConfigured"]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: is_alipay_clearing_configured
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

支付宝清分配置标识表示租户是否已配置支付宝清分。configured 与 isAlipayClearingConfigured 同义，缺省为 FALSE。

## 需求背景

查询结果需要明确响应配置状态，缺省值保证安全。

## 版本演进

初始定义，暂无变更。边界说明来自语义分析 term_bridges。

[[tables/ProjectAlipayClearingConfigRespDTO]] [[rules/支付宝清分配置结果缺省值]]