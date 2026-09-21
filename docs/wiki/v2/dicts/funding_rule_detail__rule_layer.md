---
type: dict
title: funding_rule_detail.rule_layer
page_key: funding_rule_detail__rule_layer
belong: dicts
status: draft
anchors: [funding_rule_detail.rule_layer]
sources: ['database_profile:funding_rule_detail.rule_layer']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [funding_rule_detail]
---

# funding_rule_detail.rule_layer

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `funding_rule_detail.rule_layer`，表页 [[tables/funding_rule_detail]]。

## 取值

```ground:dict
dict: funding_rule_detail__rule_layer
fields: [funding_rule_detail.rule_layer]
values:
  FINANCING: {trust: proposed}
  UNDERLYING: {trust: proposed}
  OTHER: {trust: proposed}
triage: hold
needs_review: true
```
