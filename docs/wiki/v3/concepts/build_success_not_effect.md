---
type: concept
title: 认证成功不等于生效
page_key: build_success_not_effect
belong: concepts
domain: cust
status: draft
aliases: [建档成功, 认证成功企业]
maps_to: cust_company_info.cust_build_status
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status]
sources: ['code_path:CustSyncEventProcessor.java:1052', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [effective_company_term, reauth_reset]
adjudication: boundary
---

# 认证成功不等于生效

BUILD_SUCCESS 只表示建档/认证成功。EFFECT 才是生效。
运营建档回调先写 BUILD_SUCCESS，再 effectCust 写 EFFECT。问有效企业必须两列一起过滤。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__cust_build_status]]
- [[dicts/cust_company_info__cust_status]]
- [[processes/cust_company_info__cust_build_status]]
- [[processes/cust_company_info__cust_status]]
- [[concepts/effective_company_term]]
- [[concepts/reauth_reset]]
