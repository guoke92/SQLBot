---
type: dict
title: wechat_project_approval_apply.project_type
page_key: wechat_project_approval_apply__project_type
belong: dicts
status: draft
anchors: [wechat_project_approval_apply.project_type]
sources: ['database_profile:wechat_project_approval_apply.project_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [wechat_project_approval_apply]
---

# wechat_project_approval_apply.project_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `wechat_project_approval_apply.project_type`，表页 [[tables/wechat_project_approval_apply]]。

## 取值

```ground:dict
dict: wechat_project_approval_apply__project_type
fields: [wechat_project_approval_apply.project_type]
values:
  SUB: {trust: proposed}
  MAIN: {trust: proposed}
triage: keep
```
