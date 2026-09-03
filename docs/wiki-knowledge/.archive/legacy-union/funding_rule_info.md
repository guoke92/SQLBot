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
title: 资方规则主表（一产品一资方一行）。
page_key: funding_rule_info
domain: 资金方规则
aliases:
- funding_rule_info
anchors:
- funding_rule_info
---
# funding_rule_info

资方规则主表（一产品一资方一行）。

```ground:table
table: funding_rule_info
description: 资方规则主表（一产品一资方一行）。
inactive: false
fields:
- name: funding_party_mark
- name: product_code
- name: rule_status
  dictionary: rule-status
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
