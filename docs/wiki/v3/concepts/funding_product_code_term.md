---
type: concept
title: 资方规则产品码
page_key: funding_product_code_term
belong: concepts
domain: funding_rule
status: draft
aliases: [funding product_code, 资方产品码]
maps_to: funding_rule_info.product_code
field_targets: [funding_rule_info.product_code, funding_rule_detail.product_code,
  funding_rule_front_cfg.product_code, funding_exception_resolution.product_code]
sources: ['field_semantics:funding_product_code_biz']
created: '2026-09-22'
updated: '2026-09-22'
contract_version: '0.1'
related: [funding_rule_info, funding_rule_detail]
also_confused_with: [platform_product_code_term, tenant_menu_product_code_term]
adjudication: boundary
semantic_kind: same_semantic
join_hint: high_overlap_ok
---

# 资方规则产品码

资方规则族内拷贝的产品业务码，常与平台产品业务码同形同源，但是**资方配置场景**切片。

- 真外键仍以 `funding_rule_info.id → *.rule_info_id` / `code → fund_rule_code_ref` 为主。
- `product_code`：hub→明细重合高可强连；与菜单/审批表同名同义时先看重合，低则只留术语。

## 页面链接

- [[tables/funding_rule_info]]
- [[tables/funding_rule_detail]]
- [[concepts/platform_product_code_term]]
- [[concepts/tenant_menu_product_code_term]]
