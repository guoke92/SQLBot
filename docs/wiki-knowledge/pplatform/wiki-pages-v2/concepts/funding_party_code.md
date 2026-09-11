---
type: concept
title: 对接方标识（fundingPartyCode）
page_key: concepts/funding_party_code
domain: funding
status: draft
aliases:
  - fundingPartyCode
  - funding_party_code
  - 对接方标识
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication"
  - "code:FundRuleInfoApplication"
contract_version: "0.1"
maps_to: "funding_exception_resolution.funding_party_code = 资方RPC 返回的 fundingKey"
field_targets:
  - funding_exception_resolution.funding_party_code
adjudication: boundary
also_confused_with:
  - 资金方标识(fundingPartyMark)
  - 资金方名称(fundingPartyName)
boundary: "异常解析表用 funding_party_code 承载资方 fundingKey；规则表用 funding_party_mark 承载同一 fundingKey，命名不同但语义同源，禁止跨表混用字段名。异常解析导入还允许填「资金方名称-fundingKey」组合串再映射为 fundingKey"
sources: ["enrich:wiki-admin"]
---

# 对接方标识（fundingPartyCode）

## 业务定位

「对接方标识」= **资方 RPC 返回的 fundingKey**，是资方在系统中的唯一键。它在两处表结构中用**不同字段名**落地：

- [[tables/funding_exception_resolution]] → `funding_party_code`
- [[tables/funding_rule_info]] / [[tables/funding_rule_detail]] → `funding_party_mark`

两者语义同源、命名不同，**跨表不可混用字段名**。此外，异常解析的导入模板允许运营填「资金方名称-fundingKey」组合串，系统先做名称映射再落库为 fundingKey；而规则侧是直接使用 fundingKey。

## 需求背景

无语义分析挂载的需求文档锚点。该术语边界由代码证据裁定：异常解析侧存在组合串映射逻辑，规则侧不存在。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/funding_key]]、[[concepts/funding_party]]、[[concepts/product_code]]
- 表：[[tables/funding_exception_resolution]]、[[tables/funding_rule_info]]

相关：[[funding_exception_resolution]]
