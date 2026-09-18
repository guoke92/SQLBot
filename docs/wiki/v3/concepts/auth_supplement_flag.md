---
type: concept
title: 企业授权书补签开关
page_key: auth_supplement_flag
belong: concepts
domain: cust
status: draft
aliases: [授权书补签逻辑优化, 是否授权书补签]
maps_to: cust_company_info.auth_aggrement_supplement_flag
field_targets: [cust_company_info.auth_aggrement_supplement_flag]
sources: ['code_path:CustAuthAgreementDomainService.java:564', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [auth_channel_flag, cross_tenant_resign, authorization_book, electronic_auth_flag]
adjudication: boundary
---

# 企业授权书补签开关

document_claim:授权书补签逻辑优化.md#31：企业维度开关，可关旧渠道误触发的补签。catalog 注释「是否授权书补签标识」。
现网 Y 需要补签，接口对 Y/N 翻转。不是租户跨贴牌 sign_flag，也不是授权确认书行。Y/N 不编字典页。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__auth_aggrement_supplement_flag]]
- [[concepts/auth_channel_flag]]
- [[concepts/authorization_book]]
- [[concepts/cross_tenant_resign]]
- [[concepts/electronic_auth_flag]]
