---
type: enum
title: rule_layer
page_key: rule_layer
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# rule_layer

（权威枚举页：3 值，绑定方式 exact-name，主承载 funding_rule_detail.rule_layer；db 实测分布。）

```ground:enum
enum: rule_layer
fields: [funding_rule_detail.rule_layer, funding_rule_front_cfg.rule_layer]
values:
  UNDERLYING:
    label: 底层规则
  FINANCING:
    label: 融资规则
  OTHER:
    label: 其他规则
```
