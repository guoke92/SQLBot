---
type: dict
title: authorization_agreement.app_tenant_code
page_key: authorization_agreement__app_tenant_code
belong: dicts
status: draft
anchors: [authorization_agreement.app_tenant_code]
sources: ['database_profile:authorization_agreement.app_tenant_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [authorization_agreement]
---

# authorization_agreement.app_tenant_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `authorization_agreement.app_tenant_code`，表页 [[tables/authorization_agreement]]。

## 取值

```ground:dict
dict: authorization_agreement__app_tenant_code
fields: [authorization_agreement.app_tenant_code]
values:
  base: {trust: proposed}
  common: {trust: proposed}
  QA2tiepai2: {trust: proposed}
  JHYL: {trust: proposed}
  LLS: {trust: proposed}
triage: hold
needs_review: true
```
