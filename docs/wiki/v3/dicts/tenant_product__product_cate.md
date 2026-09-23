---
type: dict
title: tenant_product.product_cate
page_key: tenant_product__product_cate
belong: dicts
status: draft
anchors: [tenant_product.product_cate]
sources: ['database_profile:tenant_product.product_cate', 'database_schema:tenant_product.product_cate']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.product_cate

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_product.product_cate`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__product_cate
fields: [tenant_product.product_cate]
values:
  STRONG: {trust: proposed, label: 强确权, evidence: 'document_claim:产品产融平台语境.md#32'}
  WEAKLY: {trust: proposed, label: 弱确权, evidence: 'document_claim:产品产融平台语境.md#32'}
  CREDIT: {trust: proposed, label: 信用类, evidence: 'document_claim:产品产融平台语境.md#32'}
triage: keep
```
