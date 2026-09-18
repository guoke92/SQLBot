---
type: dict
title: authorization_agreement.company_type
page_key: authorization_agreement__company_type
belong: dicts
status: draft
anchors: [authorization_agreement.company_type]
sources: ['database_profile:authorization_agreement.company_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [authorization_agreement]
---

# authorization_agreement.company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `authorization_agreement.company_type`，表页 [[tables/authorization_agreement]]。

## 取值

```ground:dict
dict: authorization_agreement__company_type
fields: [authorization_agreement.company_type]
values:
  SUPPLIER: {trust: proposed}
  CORE: {trust: proposed}
  FINANCE: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  PLATFORM_OPREATOR_COMPANY: {trust: proposed}
  CORPORATION_COMPANY: {trust: proposed}
  DEALER: {trust: proposed}
  CORE_MANAGER: {trust: proposed}
  '["CORE"]': {trust: proposed}
  '["FINANCE"]': {trust: proposed}
  '["PROJECT_COMPANY"]': {trust: proposed}
  FACTOR_COMPANY: {trust: proposed}
triage: keep
```
