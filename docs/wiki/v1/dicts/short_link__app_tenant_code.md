---
type: dict
title: short_link.app_tenant_code
page_key: short_link__app_tenant_code
belong: dicts
status: draft
anchors: [short_link.app_tenant_code]
sources: ['database_profile:short_link.app_tenant_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [short_link]
---

# short_link.app_tenant_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `short_link.app_tenant_code`，表页 [[tables/short_link]]。

## 取值

```ground:dict
dict: short_link__app_tenant_code
fields: [short_link.app_tenant_code]
values:
  base: {trust: proposed}
triage: hold
needs_review: true
```
