---
type: dict
title: async_io_task.menu_code
page_key: async_io_task__menu_code
belong: dicts
status: draft
anchors: [async_io_task.menu_code]
sources: ['database_profile:async_io_task.menu_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [async_io_task]
---

# async_io_task.menu_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `async_io_task.menu_code`，表页 [[tables/async_io_task]]。

## 取值

```ground:dict
dict: async_io_task__menu_code
fields: [async_io_task.menu_code]
values:
  PROJECT_REPORT_STATISTICS: {trust: proposed}
  WECHAT_PROJECT_APPROVAL: {trust: proposed}
  CUST_PROJECT_REL_BATCH: {trust: proposed}
  TENANT_PROJECT_CONFIG: {trust: proposed}
  CUST_INPUT_BATCH: {trust: proposed}
  PROJECT_ONLINE_APPROVAL: {trust: proposed}
triage: hold
needs_review: true
```
