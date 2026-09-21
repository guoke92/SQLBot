---
type: dict
title: cust_auth_application.open_status
page_key: cust_auth_application__open_status
belong: dicts
status: draft
anchors: [cust_auth_application.open_status]
sources: ['database_profile:cust_auth_application.open_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_auth_application]
---

# cust_auth_application.open_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_auth_application.open_status`，表页 [[tables/cust_auth_application]]。

## 取值

```ground:dict
dict: cust_auth_application__open_status
fields: [cust_auth_application.open_status]
values:
  OPENING: {trust: proposed}
  OPENED: {trust: proposed}
  NOT_OPENED: {trust: proposed}
triage: keep
```
