---
type: concept
title: 新旧渠道授权书标识
page_key: auth_channel_flag
belong: concepts
domain: cust
status: draft
aliases: [新旧渠道授权书补签]
maps_to: cust_company_info.migarory_auth_aggrement_flag
field_targets: [cust_company_info.migarory_auth_aggrement_flag]
sources: ['code_path:PlatFormMigratoryApplication.java:1687', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
also_confused_with: [auth_supplement_flag, cross_tenant_resign, direct_init_need_resign]
adjudication: boundary
---

# 新旧渠道授权书标识

catalog 注释「新旧渠道授权书补签标识，Y 新渠道:N 旧渠道」。列名拼写是 migarory。
迁移时新渠道写 Y 且补签开关 N。不是租户 sign_flag，也不是企业补签开关，也不是直推 need_resign_auth。Y/N 不编字典页。

## 页面链接

- [[tables/cust_company_info]]
- [[dicts/cust_company_info__migarory_auth_aggrement_flag]]
- [[concepts/auth_supplement_flag]]
- [[concepts/cross_tenant_resign]]
- [[concepts/direct_init_need_resign]]
