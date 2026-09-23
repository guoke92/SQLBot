---
type: dict
title: wechat_project_approval_apply.enable
page_key: wechat_project_approval_apply__enable
belong: dicts
status: draft
anchors: [wechat_project_approval_apply.enable]
sources: ['database_profile:wechat_project_approval_apply.enable', 'database_schema:wechat_project_approval_apply.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [wechat_project_approval_apply]
---

# wechat_project_approval_apply.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `wechat_project_approval_apply.enable`，表页 [[tables/wechat_project_approval_apply]]。

## 取值

```ground:dict
dict: wechat_project_approval_apply__enable
fields: [wechat_project_approval_apply.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
