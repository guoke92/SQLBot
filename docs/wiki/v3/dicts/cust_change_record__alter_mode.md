---
type: dict
title: cust_change_record.alter_mode
page_key: cust_change_record__alter_mode
belong: dicts
status: draft
anchors: [cust_change_record.alter_mode]
sources: ['database_profile:cust_change_record.alter_mode', 'database_schema:cust_change_record.alter_mode',
  'code_path:AlterModeEnum.java:10']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.alter_mode

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_change_record.alter_mode`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__alter_mode
fields: [cust_change_record.alter_mode]
values:
  '1': {trust: confirmed, label: 平台变更, evidence: 'code_path:AlterModeEnum.java:10'}
  '2': {trust: confirmed, label: 企业自行变更, evidence: 'code_path:AlterModeEnum.java:10'}
triage: hold
needs_review: true
```
