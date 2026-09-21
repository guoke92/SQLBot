---
type: concept
title: 产品类型
page_key: product_cate_term
belong: concepts
domain: remaining
status: draft
aliases: [产品大类类型, 确权类型, 强确权弱确权]
maps_to: platform_product.product_cate
field_targets: [platform_product.product_cate, tenant_product.product_cate, tenant_interworking_product.product_cate]
sources: ['document_claim:产品产融平台语境.md#32', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [platform_product, tenant_product, tenant_interworking_product]
also_confused_with: [platform_product_master, open_tenant_product_term]
adjudication: boundary
---

# 产品类型

document_claim:产品产融平台语境.md#32：产品类型枚举为强确权、弱确权、信用类。
主锚 platform_product.product_cate；租户产品/互通产品同名列是租户侧拷贝，答租户开通产品类型时用 tenant_product.product_cate。
不是「平台产品」身份码 product_code，也不是 product_type（通用/互通）。

## 页面链接

- [[tables/platform_product]]
- [[tables/tenant_interworking_product]]
- [[tables/tenant_product]]
- [[dicts/platform_product__product_cate]]
- [[dicts/tenant_interworking_product__product_cate]]
- [[dicts/tenant_product__product_cate]]
- [[concepts/open_tenant_product_term]]
- [[concepts/platform_product_master]]
