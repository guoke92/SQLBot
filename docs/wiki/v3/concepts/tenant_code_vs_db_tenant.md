---
type: concept
title: 租户码与数据租户码
page_key: tenant_code_vs_db_tenant
belong: concepts
domain: remaining
status: draft
aliases: [tenant_code, db_tenant_code, app_tenant_code, SSO租户码]
maps_to: open_sso_channel.db_tenant_code
field_targets: [open_sso_channel.db_tenant_code, open_sso_channel.tenant_code, tenant_setting_config.db_tenant_code,
  cust_app_channel_config.app_tenant_code, cust_app_channel_config.db_tenant_code]
sources: ['code_path:OpenSsoChannelDao.java:24', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [open_sso_channel, tenant_setting_config, cust_app_channel_config]
also_confused_with: [open_sso_channel_term, channel_archive_longteng, channel_code_term,
  app_channel_config_term]
adjudication: boundary
---

# 租户码与数据租户码

业务表普遍有 db_tenant_code（数据租户）与 app_tenant_code（逻辑租户）。
SSO 运行时 credential.tenantCode 取自 open_sso_channel.db_tenant_code（OpenSsoChannelService.requireRuntimeCredential → tenantCode(row.getDbTenantCode())）。
live open_sso_channel.tenant_code 与 db_tenant_code 并存；DO 字段仍是 dbTenantCode，勿与 channel_code 互代。
例外：cust_app_channel_config.app_tenant_code 存的是 channel_code（渠道码），不是租户码（见 ChannelArchiveAppChannelConfigInitializer）。

## 页面链接

- [[tables/cust_app_channel_config]]
- [[tables/open_sso_channel]]
- [[tables/tenant_setting_config]]
- [[concepts/app_channel_config_term]]
- [[concepts/channel_archive_longteng]]
- [[concepts/channel_code_term]]
- [[concepts/open_sso_channel_term]]
