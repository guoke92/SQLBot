---
type: concept
title: appId
page_key: app_id
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - app_id
  - dbassAppId
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.app_id
  - code:SaaSAuthController.java:getTenantSetting
contract_version: "0.1"
maps_to: open_sso_channel.app_id
also_confused_with:
  - tenant_setting_config.dbass_app_id
adjudication: boundary
belong: concepts
field_targets: [open_sso_channel.app_id]
sources: ["enrich:wiki-admin"]
---

appId 在开放平台渠道语境下指 [[open_sso_channel.app_id]]（开放平台 appId，DB 实测
73d62771729e4ffba7f263cb6012746d）。

## 需求背景

渠道接入开放平台需要 appId；租户配置里另有 DBAss 侧 appId（tenant_setting_config.dbass_app_id），
返回前端前被显式置 null 脱敏。

## 版本演进

- v0（草稿）：术语边界来自 DB 实测与脱敏代码。

边界：open_sso_channel.app_id 是开放平台 appId；tenant_setting_config.dbass_app_id 是 DBAss 侧 appId，
两者来源与用途不同，不可互换（见 [[dbass]]）。

相关：[[open_sso_channel]]
