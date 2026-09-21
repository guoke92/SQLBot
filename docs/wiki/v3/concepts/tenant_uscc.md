---
type: concept
title: 租户统一社会信用代码
page_key: tenant_uscc
belong: concepts
domain: tenant
status: draft
aliases: [租户统码, 租户名称和统码]
maps_to: tenant_setting_config.uni_social_credit_code
field_targets: [tenant_setting_config.uni_social_credit_code, tenant_setting_config.name]
sources: ['code_path:TenantDomainService.java:230', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [tenant_flg_en, tenant_oper_update_split]
adjudication: boundary
---

# 租户统一社会信用代码

document_claim:租户配置支持修改名称和统码.md#14：已生效租户可改名称和统码。
现网 checkBeforeSave 只校验统码格式，没有冻结后禁止修改。不要用 tenant_flg_en 或企业 certification_no 回答租户统码。

## 页面链接

- [[tables/tenant_setting_config]]
- [[concepts/tenant_flg_en]]
- [[concepts/tenant_oper_update_split]]
