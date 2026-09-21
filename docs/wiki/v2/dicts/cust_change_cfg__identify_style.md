---
type: dict
title: cust_change_cfg.identify_style
page_key: cust_change_cfg__identify_style
belong: dicts
status: draft
anchors: [cust_change_cfg.identify_style]
sources: ['database_profile:cust_change_cfg.identify_style']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_change_cfg]
---

# cust_change_cfg.identify_style

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_change_cfg.identify_style`，表页 [[tables/cust_change_cfg]]。

## 取值

```ground:dict
dict: cust_change_cfg__identify_style
fields: [cust_change_cfg.identify_style]
values:
  INVITE: {trust: proposed}
  INVITE_AGW: {trust: proposed}
  SELF: {trust: proposed}
  SIMPLE: {trust: proposed}
triage: hold
needs_review: true
```
