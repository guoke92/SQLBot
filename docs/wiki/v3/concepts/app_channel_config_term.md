---
type: concept
title: 应用渠道映射
page_key: app_channel_config_term
belong: concepts
domain: remaining
status: draft
aliases: [app渠道配置, cust_app_channel_config]
maps_to: cust_app_channel_config.app_id
field_targets: [cust_app_channel_config.app_id, cust_app_channel_config.app_tenant_code,
  cust_app_channel_config.db_tenant_code]
sources: ['code_path:ChannelArchiveAppChannelConfigInitializer.java:53', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_app_channel_config]
also_confused_with: [open_sso_channel_term, channel_archive_longteng, tenant_code_vs_db_tenant]
adjudication: boundary
---

# 应用渠道映射

建档初始化：按企业 db_tenant_code 幂等写 cust_app_channel_config；app_id 来自 open_sso_channel.app_id（UUID）。
app_tenant_code 写入 channel_code（如 longteng），不要当成租户 db_tenant_code。

## 页面链接

- [[tables/cust_app_channel_config]]
- [[dicts/cust_app_channel_config__app_id]]
- [[concepts/channel_archive_longteng]]
- [[concepts/open_sso_channel_term]]
- [[concepts/tenant_code_vs_db_tenant]]
