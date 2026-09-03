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
type: enum
title: 规则层级
page_key: rule_layer
domain: 资金方规则
aliases:
- 底层规则
- 融资规则
- 规则层级分类
anchors:
- rule_layer
---
# 规则层级

rule_layer 三值：UNDERLYING 底层规则 / FINANCING 融资规则 / OTHER 其他规则。detail 的 rule_layer 从 funding_rule_front_cfg 继承（按 frontKey 匹配），非独立写值。

```ground:enum
enum: rule_layer
fields:
- funding_rule_detail.rule_layer
values:
  UNDERLYING:
    label: 底层资产层
  FINANCING:
    label: 融资层
  OTHER:
    label: 其他
```

## 关联
- [[funding_rule_detail|funding_rule_detail]]
