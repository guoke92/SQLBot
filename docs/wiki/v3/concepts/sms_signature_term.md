---
type: concept
title: 租户短信签名
page_key: sms_signature_term
belong: concepts
domain: tenant
status: draft
aliases: [短信签名]
maps_to: tenant_setting_config.platform_sms_signature
field_targets: [tenant_setting_config.platform_sms_signature]
sources: ['code_path:TenantAppliactionService.java:176', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [customer_card_term]
adjudication: boundary
---

# 租户短信签名

document_claim:租户配置增加短信签名展示.md#14。catalog 有 platform_sms_signature。
现网租户导出签名走短信模板 getMessignature(db_tenant_code)，不是直接读该列。问列表展示的签名以导出逻辑为准。

## 页面链接

- [[tables/tenant_setting_config]]
- [[concepts/customer_card_term]]
