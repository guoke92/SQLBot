---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:funding-party-rules@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: 资方规则前端配置模板（定义可配置的规则项及其渲染方式）。
page_key: funding_rule_front_cfg
domain: 资金方规则
aliases:
- funding_rule_front_cfg
anchors:
- funding_rule_front_cfg
---
# funding_rule_front_cfg

资方规则前端配置模板（定义可配置的规则项及其渲染方式）。

```ground:table
table: funding_rule_front_cfg
description: 资方规则前端配置模板（定义可配置的规则项及其渲染方式）。
inactive: false
fields: []
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.rule_key
right: funding_rule_front_cfg.front_key
cardinality: many_to_one
status: proposed
evidence: code_path:ev-fpr-rule-status
```
