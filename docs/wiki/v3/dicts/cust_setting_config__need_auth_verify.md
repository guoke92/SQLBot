---
type: dict
title: cust_setting_config.need_auth_verify
page_key: cust_setting_config__need_auth_verify
belong: dicts
status: draft
anchors: [cust_setting_config.need_auth_verify]
sources: ['database_profile:cust_setting_config.need_auth_verify']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_setting_config]
---

# cust_setting_config.need_auth_verify

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_setting_config.need_auth_verify`，表页 [[tables/cust_setting_config]]。

## 取值

```ground:dict
dict: cust_setting_config__need_auth_verify
fields: [cust_setting_config.need_auth_verify]
values:
  'yes': {trust: proposed}
triage: hold
needs_review: true
```
