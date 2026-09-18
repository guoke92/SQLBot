---
type: dict
title: tenant_project.platform_product_code
page_key: tenant_project__platform_product_code
belong: dicts
status: draft
anchors: [tenant_project.platform_product_code]
sources: ['database_profile:tenant_project.platform_product_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.platform_product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project.platform_product_code`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__platform_product_code
fields: [tenant_project.platform_product_code]
values:
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  ORDER: {trust: proposed}
  BEECREDIT: {trust: proposed}
  DRAFT: {trust: proposed}
  STORAGE: {trust: proposed}
  DRAFTQA: {trust: proposed}
  VOUCHER: {trust: proposed}
triage: keep
```
