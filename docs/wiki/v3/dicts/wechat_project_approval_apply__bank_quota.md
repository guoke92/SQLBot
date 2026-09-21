---
type: dict
title: wechat_project_approval_apply.bank_quota
page_key: wechat_project_approval_apply__bank_quota
belong: dicts
status: draft
anchors: [wechat_project_approval_apply.bank_quota]
sources: ['database_profile:wechat_project_approval_apply.bank_quota']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [wechat_project_approval_apply]
---

# wechat_project_approval_apply.bank_quota

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `wechat_project_approval_apply.bank_quota`，表页 [[tables/wechat_project_approval_apply]]。

## 取值

```ground:dict
dict: wechat_project_approval_apply__bank_quota
fields: [wechat_project_approval_apply.bank_quota]
values:
  1000万: {trust: proposed}
  100万: {trust: proposed}
  '1000': {trust: proposed}
  '10000': {trust: proposed}
  '4324324': {trust: proposed}
  '100': {trust: proposed}
  '200000': {trust: proposed}
  '1234567890': {trust: proposed}
  '333': {trust: proposed}
  2000万: {trust: proposed}
  '222': {trust: proposed}
  '100000': {trust: proposed}
triage: hold
needs_review: true
```
