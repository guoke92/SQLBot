---
type: dict
title: tenant_interworking_product.scope_role
page_key: tenant_interworking_product__scope_role
belong: dicts
status: draft
anchors: [tenant_interworking_product.scope_role]
sources: ['database_profile:tenant_interworking_product.scope_role']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_interworking_product]
---

# tenant_interworking_product.scope_role

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `tenant_interworking_product.scope_role`，表页 [[tables/tenant_interworking_product]]。

## 取值

```ground:dict
dict: tenant_interworking_product__scope_role
fields: [tenant_interworking_product.scope_role]
values:
  '["SUPPLIER"]': {trust: proposed}
  '["FINANCE"]': {trust: proposed}
  '["PROJECT_COMPANY","CORE"]': {trust: proposed}
  '["PROJECT_COMPANY"]': {trust: proposed}
  '["CORE","PROJECT_COMPANY"]': {trust: proposed}
triage: hold
needs_review: true
```
