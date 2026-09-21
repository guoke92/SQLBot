---
type: dict
title: ca_fee_order.version
page_key: ca_fee_order__version
belong: dicts
status: draft
anchors: [ca_fee_order.version]
sources: ['database_profile:ca_fee_order.version']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [ca_fee_order]
---

# ca_fee_order.version

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `ca_fee_order.version`，表页 [[tables/ca_fee_order]]。

## 取值

```ground:dict
dict: ca_fee_order__version
fields: [ca_fee_order.version]
values:
  '1': {trust: proposed}
  '0': {trust: proposed}
  '2': {trust: proposed}
  '3': {trust: proposed}
  '5': {trust: proposed}
  '4': {trust: proposed}
  '6': {trust: proposed}
  '7': {trust: proposed}
  '8': {trust: proposed}
  '18': {trust: proposed}
  '9': {trust: proposed}
triage: hold
needs_review: true
```
