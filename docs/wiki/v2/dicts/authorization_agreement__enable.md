---
type: dict
title: authorization_agreement.enable
page_key: authorization_agreement__enable
belong: dicts
status: draft
anchors: [authorization_agreement.enable]
sources: ['database_profile:authorization_agreement.enable']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [authorization_agreement]
---

# authorization_agreement.enable

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `authorization_agreement.enable`，表页 [[tables/authorization_agreement]]。

## 取值

```ground:dict
dict: authorization_agreement__enable
fields: [authorization_agreement.enable]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: keep
```
