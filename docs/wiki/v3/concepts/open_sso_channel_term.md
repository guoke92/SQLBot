---
type: concept
title: 开放登录SSO渠道
page_key: open_sso_channel_term
belong: concepts
domain: remaining
status: draft
aliases: [SSO渠道, 龙腾渠道, longteng, 本地化渠道]
maps_to: open_sso_channel.channel_code
field_targets: [open_sso_channel.channel_code, open_sso_channel.db_tenant_code, open_sso_channel.tenant_code,
  open_sso_channel.app_id]
sources: ['code_path:ChannelArchiveAppChannelConfigInitializer.java:94', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [open_sso_channel]
also_confused_with: [channel_code_term, channel_archive_longteng, default_push_project,
  tenant_code_vs_db_tenant, app_channel_config_term]
adjudication: boundary
---

# 开放登录SSO渠道

渠道主数据在 open_sso_channel。channel_code 是 OpenAPI/建档渠道标识（如 longteng）。
channel_kind=LOCAL_SYS/STANDARD 是渠道类型，不是 channel_code 本身。
运行时 SSO tenantCode 取自 db_tenant_code；live 另有 tenant_code 列。
不是 tenant_project.channel_code（项目邀请码），也不是 cust_project_rel.channel_code。
cust_app_channel_config.app_id 必须是开放平台 UUID，从 open_sso_channel 解析，禁止用 channel_code 冒充 appId。
CustPersonInfoSourceEnum.longteng=龙腾 是人员来源，不是本表 channel_code。

## 页面链接

- [[tables/open_sso_channel]]
- [[dicts/open_sso_channel__app_id]]
- [[dicts/open_sso_channel__channel_code]]
- [[concepts/app_channel_config_term]]
- [[concepts/channel_archive_longteng]]
- [[concepts/channel_code_term]]
- [[concepts/default_push_project]]
- [[concepts/tenant_code_vs_db_tenant]]
