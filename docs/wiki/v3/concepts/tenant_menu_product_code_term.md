---
type: concept
title: 租户菜单产品码
page_key: tenant_menu_product_code_term
belong: concepts
domain: tenant
status: draft
aliases: [菜单产品码]
maps_to: tenant_product_menu.product_code
field_targets: [tenant_product_menu.product_code, tenant_product_menu_res.product_code]
sources: ['field_semantics:tenant_menu_product_code']
created: '2026-09-22'
updated: '2026-09-22'
contract_version: '0.1'
related: [tenant_product_menu, tenant_product_menu_res]
also_confused_with: [platform_product_code_term, funding_product_code_term]
adjudication: boundary
semantic_kind: same_semantic
join_hint: high_overlap_ok
---

# 租户菜单产品码

菜单与按钮同行场景下的产品码拷贝；与 `menu_id` 一并构成菜单族业务键。

与平台/资方 `product_code` **同名同义**，但不默认跨场景互链——重合高才 EQUI_JOIN。

## 页面链接

- [[tables/tenant_product_menu]]
- [[tables/tenant_product_menu_res]]
- [[concepts/platform_product_code_term]]
- [[concepts/funding_product_code_term]]
