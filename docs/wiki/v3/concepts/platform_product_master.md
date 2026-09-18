---
type: concept
title: 平台产品
page_key: platform_product_master
belong: concepts
domain: remaining
status: draft
aliases: [产品大类, 平台产品目录]
maps_to: platform_product.product_code
field_targets: [platform_product.product_code, platform_product.product_status]
sources: ['code_path:PlatformProductDaoImpl.java:111', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [platform_product]
also_confused_with: [open_tenant_product_term]
adjudication: boundary
---

# 平台产品

平台侧产品主数据。已生效是 product_status=1 且 enable=Y。
租户是否开通看 tenant_product.open_status，不要和平台产品状态互代。

## 页面链接

- [[tables/platform_product]]
- [[dicts/platform_product__product_code]]
- [[dicts/platform_product__product_status]]
- [[processes/platform_product__product_status]]
- [[concepts/open_tenant_product_term]]
