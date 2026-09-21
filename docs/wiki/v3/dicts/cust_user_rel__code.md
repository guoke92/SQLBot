---
type: dict
title: cust_user_rel.code
page_key: cust_user_rel__code
belong: dicts
status: draft
anchors: [cust_user_rel.code]
sources: ['database_profile:cust_user_rel.code']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_user_rel]
---

# cust_user_rel.code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_user_rel.code`，表页 [[tables/cust_user_rel]]。

## 取值

```ground:dict
dict: cust_user_rel__code
fields: [cust_user_rel.code]
values:
  a: {trust: proposed}
triage: hold
needs_review: true
```
