---
type: dict
title: cust_setting_config.code
page_key: cust_setting_config__code
belong: dicts
status: draft
anchors: [cust_setting_config.code]
sources: ['database_profile:cust_setting_config.code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_setting_config]
---

# cust_setting_config.code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_setting_config.code`，表页 [[tables/cust_setting_config]]。

## 取值

```ground:dict
dict: cust_setting_config__code
fields: [cust_setting_config.code]
values:
  '9999999999': {trust: proposed}
triage: hold
needs_review: true
```
