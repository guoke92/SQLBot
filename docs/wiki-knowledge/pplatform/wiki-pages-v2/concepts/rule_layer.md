---
type: concept
title: 规则层级（ruleLayer）
page_key: rule_layer
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则层
  - ruleLayer
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_detail
  - db:funding_rule_front_cfg
maps_to: funding_rule_detail.rule_layer
field_targets:
  - funding_rule_detail.rule_layer
  - funding_rule_front_cfg.rule_layer
adjudication: synonym
also_confused_with:
  - funding_rule_front_cfg.rule_layer
contract_version: "0.1"
belong: concepts
field_targets: [funding_rule_detail.rule_layer]
---

规则层级描述一条规则字段属于底层（UNDERLYING）/ 融资（FINANCING）/ 其他（OTHER）哪一层。配置侧在 [[funding_rule_front_cfg]] 定义，明细侧在 [[funding_rule_detail]] 保存时从 frontCfg 复制，**同值但不是外键关系**。

## 需求背景

- 导入阶段 4 需把规则层级的 displayName 翻译为 dictKey，并参与 (product, rule_layer, key_name) 三元组定位 frontKey（[[rule_import_four_stage_validation]]）。
- 对外 Provider 正是按本字段把明细聚合成三组返回（[[rule_provider_active_only]]）；实测取值分布见 [[funding_rule_detail_rule_layer_scope]]。

## 版本演进

v0 首次建立，判定类型 synonym，边界为「配置侧定义、明细侧复制，非外键」。