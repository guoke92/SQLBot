---
type: dict
title: cust_change_record.oper_channel
page_key: cust_change_record__oper_channel
belong: dicts
status: draft
anchors: [cust_change_record.oper_channel]
sources: ['database_profile:cust_change_record.oper_channel', 'database_schema:cust_change_record.oper_channel',
  'code_path:DirectInitAccessModes.java:10']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.oper_channel

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_change_record.oper_channel`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__oper_channel
fields: [cust_change_record.oper_channel]
values:
  operation-pplatform-common-new: {trust: proposed}
  operation-pplatform-not-edit-new: {trust: proposed}
  DIRECT_INIT: {trust: confirmed, label: 方案2直推, evidence: 'code_path:DirectInitAccessModes.java:10'}
triage: hold
needs_review: true
```
