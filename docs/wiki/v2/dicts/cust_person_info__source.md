---
type: dict
title: cust_person_info.source
page_key: cust_person_info__source
belong: dicts
status: draft
anchors: [cust_person_info.source]
sources: ['database_profile:cust_person_info.source']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.source

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_person_info.source`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__source
fields: [cust_person_info.source]
values:
  longteng: {trust: proposed}
  AMS: {trust: proposed}
  jingke: {trust: proposed}
triage: hold
needs_review: true
```
