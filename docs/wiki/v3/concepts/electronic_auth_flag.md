---
type: concept
title: 生成电子版授权书
page_key: electronic_auth_flag
belong: concepts
domain: tenant
status: draft
aliases: [线下授权书电子版, 电子授权书开关]
maps_to: tenant_setting_config.generate_electronic_auth_flag
field_targets: [tenant_setting_config.generate_electronic_auth_flag]
sources: ['code_path:ElectronicAuthLetterApplication.java:49', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [authorization_book, cross_tenant_resign, auth_supplement_flag,
  direct_init_need_resign, electronic_auth_sign_status_term]
adjudication: boundary
---

# 生成电子版授权书

document_claim:线下授权书自动生成电子版.md#32：租户运营配置「生成电子版授权书」。
现网按 db_tenant_code 且 enable=Y 读 generate_electronic_auth_flag=Y。Y/N 不编字典页。
不是 authorization_agreement 那张授权确认书行，也不是 cust_*_record.electronic_auth_sign_status，也不是直推 need_resign_auth。

## 页面链接

- [[tables/tenant_setting_config]]
- [[dicts/tenant_setting_config__generate_electronic_auth_flag]]
- [[concepts/auth_supplement_flag]]
- [[concepts/authorization_book]]
- [[concepts/cross_tenant_resign]]
- [[concepts/direct_init_need_resign]]
- [[concepts/electronic_auth_sign_status_term]]
