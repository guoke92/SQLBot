---
type: dict
title: authorization_agreement.creation_type
page_key: authorization_agreement__creation_type
belong: dicts
status: draft
anchors: [authorization_agreement.creation_type]
sources: ['database_profile:authorization_agreement.creation_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [authorization_agreement]
---

# authorization_agreement.creation_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `authorization_agreement.creation_type`，表页 [[tables/authorization_agreement]]。

## 取值

```ground:dict
dict: authorization_agreement__creation_type
fields: [authorization_agreement.creation_type]
values:
  CUST_BUILD_INIT: {trust: proposed}
  AUTO: {trust: proposed}
  COMPANY_MANAGER_CHANGE_CODE: {trust: proposed}
triage: keep
```
