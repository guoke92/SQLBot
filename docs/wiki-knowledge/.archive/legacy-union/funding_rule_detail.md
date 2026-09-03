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
title: 资方规则 KV 明细（一行=一个规则项）。
page_key: funding_rule_detail
domain: 资金方规则
aliases:
- funding_rule_detail
anchors:
- funding_rule_detail
---
# funding_rule_detail

资方规则 KV 明细（一行=一个规则项）。

```ground:table
table: funding_rule_detail
description: 资方规则 KV 明细（一行=一个规则项）。
inactive: false
fields:
- name: rule_info_id
- name: rule_key
- name: rule_layer
  dictionary: rule-layer
- name: rule_value
- name: version
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.rule_info_id
right: funding_rule_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-fpr-rule-status
```

```ground:relation
type: EQUI_JOIN
left: funding_rule_detail.rule_key
right: funding_rule_front_cfg.front_key
cardinality: many_to_one
status: proposed
evidence: code_path:ev-fpr-rule-status
```
