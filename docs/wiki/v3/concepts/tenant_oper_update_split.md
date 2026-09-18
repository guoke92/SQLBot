---
type: concept
title: 租户运营配置更新人
page_key: tenant_oper_update_split
belong: concepts
domain: tenant
status: draft
aliases: [运营配置更新人分离, op_update_user]
maps_to: tenant_setting_config.op_update_user
field_targets: [tenant_setting_config.op_update_user, tenant_setting_config.op_update_time]
sources: ['code_path:TenantSettingConfigController.java:114', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [tenant_uscc, customer_card_term]
adjudication: boundary
---

# 租户运营配置更新人

document_claim:租户配置更新人分离.md#15：运营配置不覆盖标准 update_user。
现网 updateOperationConfigById 把原 update_user 写入 op_update_user，不改标准更新人。问运营配置谁改的看 op_update_*。

## 页面链接

- [[tables/tenant_setting_config]]
- [[concepts/customer_card_term]]
- [[concepts/tenant_uscc]]
