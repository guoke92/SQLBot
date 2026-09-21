---
type: dict
title: cust_change_record.legal_auth
page_key: cust_change_record__legal_auth
belong: dicts
status: draft
anchors: [cust_change_record.legal_auth]
sources: ['database_profile:cust_change_record.legal_auth']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.legal_auth

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_change_record.legal_auth`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__legal_auth
fields: [cust_change_record.legal_auth]
values:
  N: {trust: proposed}
  Y: {trust: proposed}
triage: hold
needs_review: true
```
