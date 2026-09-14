---
type: concept
title: 白名单
page_key: whitelist
domain: CA证书收费
status: draft
aliases:
  - WHITELIST
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
maps_to: ca_fee_company.special_config_flag
field_targets:
  - ca_fee_company.special_config_flag
  - ca_fee_project_config.special_company_list
adjudication: boundary
boundary: 企业快照用于规则快速判断；项目 JSON 是配置源，二者需交叉校验
also_confused_with:
  - ca_fee_project_config.special_company_list
belong: concepts
field_targets: [ca_fee_company.special_config_flag]
sources: ["enrich:wiki-admin"]
---

「白名单」在企业侧表现为特殊配置快照标记 `ca_fee_company.special_config_flag = 'Y'`（口径 [[company_special_config_flag]]），在项目侧表现为 `ca_fee_project_config.special_company_list` JSON 中的 `WHITELIST` 条目。

**边界（易混淆）**：企业快照只用于规则引擎的**快速判断**，项目 JSON 才是**配置源**；两者必须交叉校验后才产生豁免结论，见 [[whitelist_exempt]]。仅凭企业快照为 `Y` 不足以豁免。

## 需求背景

规则引擎在缴费校验链路上被高频调用，需要企业级快照降低配置读取成本；同时配置的变更入口在运营后台的项目维度，故保留双写并要求交叉校验。

## 版本演进

- v0（本页）：建立术语桥与边界。

相关：[[ca_fee_company]]
