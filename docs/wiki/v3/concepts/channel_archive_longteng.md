---
type: concept
title: 龙腾渠道建档
page_key: channel_archive_longteng
belong: concepts
domain: cust
status: draft
aliases: [longteng建档, 渠道建档, OpenAPI建档]
maps_to: cust_company_info.channel_code
field_targets: [cust_company_info.channel_code, cust_access_secret.channel, open_sso_channel.channel_code]
sources: ['code_path:ChannelArchiveAppChannelConfigInitializer.java:44', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info, cust_access_secret, open_sso_channel]
also_confused_with: [invite_customer_entry, default_push_project, open_sso_channel_term,
  channel_code_term, app_channel_config_term, tenant_code_vs_db_tenant, channel_code_homonym_bundle]
adjudication: boundary
---

# 龙腾渠道建档

渠道码 longteng 等为 open_sso_channel.channel_code / 企业 channel_code / cust_access_secret.channel。
CustPersonInfoSourceEnum.longteng displayName=龙腾 是人员来源，不是 oper_channel，也不是 channel_kind。
建档时常挂载 cust_app_channel_config（app_tenant_code=channel_code，app_id=开放平台 UUID）。

## 页面链接

- [[tables/cust_access_secret]]
- [[tables/cust_company_info]]
- [[tables/open_sso_channel]]
- [[dicts/cust_access_secret__channel]]
- [[dicts/cust_company_info__channel_code]]
- [[dicts/open_sso_channel__channel_code]]
- [[concepts/app_channel_config_term]]
- [[concepts/channel_code_term]]
- [[concepts/default_push_project]]
- [[concepts/invite_customer_entry]]
- [[concepts/open_sso_channel_term]]
- [[concepts/tenant_code_vs_db_tenant]]
