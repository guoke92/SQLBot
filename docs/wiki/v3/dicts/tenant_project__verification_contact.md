---
type: dict
title: tenant_project.verification_contact
page_key: tenant_project__verification_contact
belong: dicts
status: draft
anchors: [tenant_project.verification_contact]
sources: ['database_profile:tenant_project.verification_contact']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.verification_contact

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project.verification_contact`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__verification_contact
fields: [tenant_project.verification_contact]
values:
  '360': {trust: proposed}
  '333': {trust: proposed}
  '404': {trust: proposed}
  OP001: {trust: proposed}
  '430': {trust: proposed}
  '383': {trust: proposed}
triage: hold
needs_review: true
```
