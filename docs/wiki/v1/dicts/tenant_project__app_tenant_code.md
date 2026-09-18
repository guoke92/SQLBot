---
type: dict
title: tenant_project.app_tenant_code
page_key: tenant_project__app_tenant_code
belong: dicts
status: draft
anchors: [tenant_project.app_tenant_code]
sources: ['database_profile:tenant_project.app_tenant_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.app_tenant_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `tenant_project.app_tenant_code`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__app_tenant_code
fields: [tenant_project.app_tenant_code]
values:
  base: {trust: proposed}
  JYYL: {trust: proposed}
  boscxsbl: {trust: proposed}
  sdhsg: {trust: proposed}
  QA2tiepai2: {trust: proposed}
  chenguang: {trust: proposed}
  reversefactoring: {trust: proposed}
  hylg: {trust: proposed}
  boscxyc: {trust: proposed}
  GREENTOWNAT: {trust: proposed}
  Liugongscf: {trust: proposed}
  YINHEKEJI: {trust: proposed}
  JHYL: {trust: proposed}
  shanghaiyinhang: {trust: proposed}
  NAURA: {trust: proposed}
triage: hold
needs_review: true
```
