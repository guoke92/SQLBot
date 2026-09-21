---
type: dict
title: funding_rule_front_cfg.rule_layer
page_key: funding_rule_front_cfg__rule_layer
belong: dicts
status: draft
anchors: [funding_rule_front_cfg.rule_layer]
sources: ['database_profile:funding_rule_front_cfg.rule_layer', 'database_schema:funding_rule_front_cfg.rule_layer',
  'code_path:RuleLayerEnum.java:18', 'code_path:RuleLayerEnum.java:17', 'code_path:RuleLayerEnum.java:19']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [funding_rule_front_cfg]
---

# funding_rule_front_cfg.rule_layer

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `funding_rule_front_cfg.rule_layer`，表页 [[tables/funding_rule_front_cfg]]。

## 取值

```ground:dict
dict: funding_rule_front_cfg__rule_layer
fields: [funding_rule_front_cfg.rule_layer]
values:
  FINANCING: {trust: confirmed, label: 融资规则, evidence: 'code_path:RuleLayerEnum.java:18'}
  UNDERLYING: {trust: confirmed, label: 底层规则, evidence: 'code_path:RuleLayerEnum.java:17'}
  OTHER: {trust: confirmed, label: 其他规则, evidence: 'code_path:RuleLayerEnum.java:19'}
triage: hold
needs_review: true
```
