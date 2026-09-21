---
type: dict
title: tenant_interworking_product.max_financing_period
page_key: tenant_interworking_product__max_financing_period
belong: dicts
status: draft
anchors: [tenant_interworking_product.max_financing_period]
sources: ['database_profile:tenant_interworking_product.max_financing_period']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_interworking_product]
---

# tenant_interworking_product.max_financing_period

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_interworking_product.max_financing_period`，表页 [[tables/tenant_interworking_product]]。

## 取值

```ground:dict
dict: tenant_interworking_product__max_financing_period
fields: [tenant_interworking_product.max_financing_period]
values:
  '6': {trust: proposed}
  1-3年: {trust: proposed}
  HTCP15: {trust: proposed}
triage: hold
needs_review: true
```
