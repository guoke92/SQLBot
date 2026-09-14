---
type: rule
title: 资方规则导入四阶段校验
page_key: rule_import_four_stage_validation
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则导入四阶段
  - 规则导入校验链
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_detail
  - db:funding_rule_front_cfg
contract_version: "0.1"
belong: rules
---

规则导入依次经过必填校验、产品枚举校验、资方 RPC 校验、规则层级与前端配置反查四个阶段，任一失败不落库；全部通过后按 (productCode, fundingPartyMark) 分组调用 saveRuleInfo。

## 需求背景

该链路与异常解析导入共享「全量校验通过才入库」的失败语义（[[exception_import_all_or_nothing]]）。阶段 4 要求规则层级能由 displayName 翻译为 dictKey，并按 (product, rule_layer, key_name) 三元组在 [[funding_rule_front_cfg]] 中反查 frontKey；落库时组内 ruleMap.key = frontKey、value = ruleValue，写入 [[funding_rule_detail]]。资方校验阶段的硬编码问题见 [[rule_import_funding_party_hardcoded]]。

## 版本演进

v0 首次建立。

```ground:rule
name: 资方规则导入四阶段校验
content: 阶段1 Excel 必填（产品/资方标识code/规则层级/规则名称/规则值）→ 阶段2 productCode 枚举 → 阶段3 资方标识 RPC 校验 → 阶段4 规则层级 displayName→dictKey 且按 (product,rule_layer,key_name) 反查 funding_rule_front_cfg 拿 frontKey；任一失败不落库；通过后按 (productCode,fundingPartyMark) 分组调 saveRuleInfo。
impact: 导入按组写入，组内 ruleMap.key=frontKey、value=ruleValue
field_targets:
  - funding_rule_detail.rule_key
  - funding_rule_detail.rule_value
  - funding_rule_front_cfg.key_name
evidence: code_path:FundRuleInfoApplication.java:importRecords/validateRuleLayerAndFrontCfg/persistFundRuleImportGroups
```