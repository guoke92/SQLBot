---
type: dict
title: platform_product.product_cate
page_key: platform_product__product_cate
belong: dicts
status: draft
anchors: [platform_product.product_cate]
sources: ['database_profile:platform_product.product_cate', 'database_schema:platform_product.product_cate']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [platform_product]
---

# platform_product.product_cate

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `platform_product.product_cate`，表页 [[tables/platform_product]]。

## 取值

```ground:dict
dict: platform_product__product_cate
fields: [platform_product.product_cate]
values:
  WEAKLY: {trust: proposed, label: 弱确权, evidence: 'document_claim:产品产融平台语境.md#32'}
  STRONG: {trust: proposed, label: 强确权, evidence: 'document_claim:产品产融平台语境.md#32'}
  CREDIT: {trust: proposed, label: 信用类, evidence: 'document_claim:产品产融平台语境.md#32'}
triage: keep
```
