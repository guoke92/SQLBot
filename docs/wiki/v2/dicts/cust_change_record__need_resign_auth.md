---
type: dict
title: cust_change_record.need_resign_auth
page_key: cust_change_record__need_resign_auth
belong: dicts
status: draft
anchors: [cust_change_record.need_resign_auth]
sources: ['database_profile:cust_change_record.need_resign_auth', 'database_schema:cust_change_record.need_resign_auth']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.need_resign_auth

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_change_record.need_resign_auth`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__need_resign_auth
fields: [cust_change_record.need_resign_auth]
values:
  Y: {trust: proposed, label: 是, evidence: 'database_schema:cust_change_record.need_resign_auth'}
  N: {trust: proposed, label: 否。直推在识别变更项时写入, evidence: 'database_schema:cust_change_record.need_resign_auth'}
triage: hold
needs_review: true
```
