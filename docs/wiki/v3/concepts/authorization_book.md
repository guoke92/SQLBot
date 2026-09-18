---
type: concept
title: 企业授权确认书
page_key: authorization_book
belong: concepts
domain: remaining
status: draft
aliases: [授权书]
maps_to: authorization_agreement.cust_id
field_targets: [authorization_agreement.cust_id, authorization_agreement.authed_status]
sources: ['code_path:AuthorizationAgreementDaoImpl.java:43', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [authorization_agreement]
also_confused_with: [agreement_migratory_term, electronic_auth_flag, add_company_role_change,
  cross_tenant_resign, auth_supplement_flag]
adjudication: boundary
---

# 企业授权确认书

授权确认书按企业主键。authed_status 为 Y/N。不是协议迁移记录表。
不是租户开关 generate_electronic_auth_flag，也不是变更项 UN0009。

## 页面链接

- [[tables/authorization_agreement]]
- [[dicts/authorization_agreement__authed_status]]
- [[concepts/add_company_role_change]]
- [[concepts/agreement_migratory_term]]
- [[concepts/auth_supplement_flag]]
- [[concepts/cross_tenant_resign]]
- [[concepts/electronic_auth_flag]]
