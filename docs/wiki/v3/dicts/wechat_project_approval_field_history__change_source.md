---
type: dict
title: wechat_project_approval_field_history.change_source
page_key: wechat_project_approval_field_history__change_source
belong: dicts
status: draft
anchors: [wechat_project_approval_field_history.change_source]
sources: ['database_profile:wechat_project_approval_field_history.change_source']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [wechat_project_approval_field_history]
---

# wechat_project_approval_field_history.change_source

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `wechat_project_approval_field_history.change_source`，表页 [[tables/wechat_project_approval_field_history]]。

## 取值

```ground:dict
dict: wechat_project_approval_field_history__change_source
fields: [wechat_project_approval_field_history.change_source]
values:
  SYNC: {trust: proposed}
  EDIT: {trust: proposed}
  MANUAL_CREATE: {trust: proposed}
  IMPORT: {trust: proposed}
  BATCH: {trust: proposed}
triage: hold
needs_review: true
```
