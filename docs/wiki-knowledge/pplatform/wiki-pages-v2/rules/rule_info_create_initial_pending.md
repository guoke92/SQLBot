---
type: rule
title: 资方规则-新增初始PENDING
page_key: rule_info_create_initial_pending
domain: funding
status: draft
aliases:
  - 新增规则默认待生效
  - 初始PENDING
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
belong: rules
---

# 资方规则-新增初始PENDING

## 业务定位

新增规则时同时落四个初始值：`rule_status=PENDING`、`version=1`、`enable='Y'`、`code=DataModelUtils.getUniqueKey()`。核心语义是「**新增规则默认未生效，必须显式生效**」——新配置不会自动对外可见，给了运营一个检视窗口。参见状态机 [[processes/funding_rule_status_machine]]。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 资方规则-新增初始PENDING
content: "新增时 rule_status=PENDING、version=1、enable='Y'、code=DataModelUtils.getUniqueKey()"
impact: "新增规则默认未生效，需显式生效"
field_targets:
  - funding_rule_info.rule_status
  - funding_rule_info.version
  - funding_rule_info.enable
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 流程：[[processes/funding_rule_status_machine]]
- 规则：[[rules/rule_info_create_duplicate_check]]、[[rules/rule_info_provider_active_only]]