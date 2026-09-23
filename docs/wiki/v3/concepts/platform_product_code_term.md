---
type: concept
title: 平台产品业务码
page_key: platform_product_code_term
belong: concepts
domain: remaining
status: draft
aliases: [platform_product_code, 产品业务码, ACFLOW类产品码]
maps_to: platform_product.product_code
field_targets: [platform_product.product_code, tenant_product.platform_product_code,
  tenant_project.platform_product_code, tenant_interworking_product.platform_product_code,
  tenant_interworking_project.platform_product_code, cust_interworking_product.platform_product_code,
  authorization_agreement.platform_product_code, cust_auth_application.platform_product_code,
  argeement_migratory_record.platform_product_code, tenant_migarory_log.platform_product_code,
  tenant_migarory_log_bak.platform_product_code]
sources: ['field_semantics:platform_product_code_biz', 'code_path:authorization_agreement.trace']
created: '2026-09-22'
updated: '2026-09-22'
contract_version: '0.1'
related: [platform_product, tenant_product, tenant_project]
also_confused_with: [platform_product_master, product_cate_term, open_tenant_product_term,
  funding_product_code_term, tenant_menu_product_code_term]
adjudication: boundary
semantic_kind: same_semantic
join_hint: high_overlap_ok
---

# 平台产品业务码

多表冗余拷贝的**同一业务字段**（如 ACFLOW），canonical 为 `platform_product.product_code`。

- **不是** `platform_product.code`（UUID 行主键码）。
- 术语层：下列 `field_targets` 均指本语义。
- JOIN：同场景/父子且 live 值域重合高（`fk_like` / 实质 `shared_domain`）时可 EQUI_JOIN，**含附属表之间 B↔C**；阶段切片导致重合低时只认语义、不强连。

## 页面链接

- [[tables/platform_product]]
- [[tables/tenant_product]]
- [[tables/tenant_project]]
- [[concepts/platform_product_master]]
- [[concepts/funding_product_code_term]]
- [[concepts/tenant_menu_product_code_term]]
- [[concepts/channel_code_homonym_bundle]]
