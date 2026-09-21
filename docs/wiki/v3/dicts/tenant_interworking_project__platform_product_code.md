---
type: dict
title: tenant_interworking_project.platform_product_code
page_key: tenant_interworking_project__platform_product_code
belong: dicts
status: draft
anchors: [tenant_interworking_project.platform_product_code]
sources: ['database_profile:tenant_interworking_project.platform_product_code']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_interworking_project]
---

# tenant_interworking_project.platform_product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_interworking_project.platform_product_code`，表页 [[tables/tenant_interworking_project]]。

## 取值

```ground:dict
dict: tenant_interworking_project__platform_product_code
fields: [tenant_interworking_project.platform_product_code]
values:
  HTCP1: {trust: proposed}
  HTCP14: {trust: proposed}
  AMS: {trust: proposed}
  HTCP13: {trust: proposed}
  HTCP5: {trust: proposed}
triage: hold
needs_review: true
```
