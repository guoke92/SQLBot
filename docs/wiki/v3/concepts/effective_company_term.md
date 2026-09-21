---
type: concept
title: 生效企业
page_key: effective_company_term
belong: concepts
domain: cust
status: draft
aliases: [有效企业, 认证成功企业]
maps_to: cust_company_info.cust_status
field_targets: [cust_company_info.cust_status, cust_company_info.cust_build_status]
sources: ['code_path:CustCompanyIfoEnchanceService.java:649', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [simple_auth, build_success_not_effect, visitor_flow_data]
adjudication: boundary
---

# 生效企业

列表「有效企业」是 BUILD_SUCCESS ∧ EFFECT ∧ 主数据 ∧ enable=Y，不是「认证方式=简易认证」，也不是单看认证成功，也不是 data_type=0 的游客/流程数据。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
- [[concepts/build_success_not_effect]]
- [[concepts/simple_auth]]
- [[concepts/visitor_flow_data]]
