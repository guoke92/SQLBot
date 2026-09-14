---
type: rule
title: 资方规则保存的版本与明细联动
page_key: rule_save_version_detail_sync
domain: 资金规则与异常处理
status: draft
aliases:
  - saveRuleInfo 版本联动
  - 规则明细 upsert
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
  - db:funding_rule_detail
contract_version: "0.1"
belong: rules
---

保存一条资方规则时，头表 [[funding_rule_info]] 与明细 [[funding_rule_detail]] 在同一动作内联动：新增走 PENDING + version=1 + 唯一 code，更新走 version+1 并覆盖资方名称，随后按 frontKey 匹配增改明细。

## 需求背景

- 新增即待生效，对外不可见，直到 activeRule（[[funding_rule_status_machine]]、[[rule_provider_active_only]]）。
- 明细匹配依据 frontKey，多出的 frontKey 静默跳过；产品无前端配置则直接抛异常（[[rule_key]]、[[funding_rule_front_cfg]]）。
- 明细判存依赖 enable='Y' 口径（[[funding_rule_detail_enable_y]]）。

## 版本演进

v0 首次建立。

```ground:rule
name: 资方规则保存的版本与明细联动
content: 新增：查重 (productCode,fundingPartyMark) → 插 funding_rule_info(ruleStatus=PENDING,version=1,code=唯一键,enable=Y)；更新：version+1 并覆盖 fundingPartyName；随后按 productCode 查 front_cfg，用 ruleMap.key 匹配 frontKey，命中已有 enable='Y' 明细则更新否则新增。
impact: ruleMap 中不存在的 frontKey 静默跳过不中断；产品无前端配置直接抛异常
field_targets:
  - funding_rule_info.version
  - funding_rule_info.rule_status
  - funding_rule_detail.rule_key
  - funding_rule_detail.rule_value
evidence: code_path:FundRuleInfoApplication.java:saveRuleInfo
```