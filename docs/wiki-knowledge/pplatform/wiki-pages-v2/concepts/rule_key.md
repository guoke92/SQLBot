---
type: concept
title: 规则字段 key（ruleKey / frontKey）
page_key: rule_key
domain: 资金规则与异常处理
status: draft
aliases:
  - frontKey
  - front_key
  - rule_key
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_detail
  - db:funding_rule_front_cfg
maps_to: funding_rule_detail.rule_key
field_targets:
  - funding_rule_detail.rule_key
  - funding_rule_front_cfg.front_key
  - funding_rule_front_cfg.rule_key
adjudication: boundary
also_confused_with:
  - funding_rule_front_cfg.rule_key
  - funding_rule_front_cfg.front_key
contract_version: "0.1"
belong: concepts
field_targets: [funding_rule_detail.rule_key]
---

三处 key 语义必须分清：[[funding_rule_detail]].rule_key 在应用层 Map 中与 [[funding_rule_front_cfg]].front_key 匹配（等价，**非 SQL JOIN**）；而 front_cfg.rule_key 是另一个字段，在 Provider 中被写成对外输出的 item.key。三者不可混用。

## 需求背景

- 规则保存：以 ruleMap.key 匹配 frontKey，命中已有 enable='Y' 明细即更新，否则新增；ruleMap 中不存在的 frontKey 静默跳过（[[rule_save_version_detail_sync]]）。
- 规则导入：按 (product, rule_layer, key_name) 反查 front_cfg 拿到 frontKey 作为明细 key（[[rule_import_four_stage_validation]]）。
- 对外输出：Provider 以 front_cfg.rule_key 作为 item.key 返回（[[rule_provider_active_only]]）。

## 版本演进

v0 首次建立，判定类型 boundary，边界为「detail.rule_key ↔ front_cfg.front_key 应用层等价；front_cfg.rule_key 是对外输出字段」。