---
type: concept
title: 租户统码
page_key: tenant_sso_chanel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sso_tenant_chanel
  - ssoTenantChanel
  - ssoTenantChannel
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserFacade.java:getSsoTenantChannel
  - code:UserInfoFacade.java:getSsoTenantChannel
  - code:LocalTypeUserController.java:listUserPage
contract_version: "0.1"
maps_to: tenant_setting_config.sso_tenant_chanel
also_confused_with:
  - open_sso_channel.sys_channel
adjudication: boundary
belong: concepts
field_targets: [tenant_setting_config.sso_tenant_chanel]
sources: ["enrich:wiki-admin"]
---

租户统码（sso_tenant_chanel / ssoTenantChanel）是租户配置里的 SSO 渠道统码，落在
[[tenant_setting_config.sso_tenant_chanel]]。

## 需求背景

用户/联系人同步 SSO 时，租户统码被作为 sysChannel 传入（UserFacade.getSsoTenantChannel、
UserInfoFacade.getSsoTenantChannel）；用户列表也把它回填到 userDTO.ssoSysChannel
（[[list_user_page_tenant_channel_backfill]]）。

## 版本演进

- v0（草稿）：术语边界来自代码赋值点。

边界：租户统码来自租户配置表，被当作 sysChannel 使用，但两者存储位置不同；不可与
[[sys_channel]]（open_sso_channel.sys_channel）互换，也不可等同于 [[db_tenant_code]]。

相关：[[tenant_setting_config]]
