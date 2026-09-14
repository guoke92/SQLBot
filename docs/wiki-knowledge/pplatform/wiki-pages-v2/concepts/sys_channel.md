---
type: concept
title: sysChannel
page_key: sys_channel
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - sys_channel
  - ssoSysChannel
  - SsoSystemDO.sysChannel
oid: 1
scope:
  databases: [unknown]
sources:
  - db:open_sso_channel.sys_channel
  - code:SaaSAuthController.java:resolveNeedLoginCaptcha
  - code:LocalTypeUserController.java:listUserPage
contract_version: "0.1"
maps_to: open_sso_channel.sys_channel
also_confused_with:
  - tenant_setting_config.sso_tenant_chanel
adjudication: boundary
belong: concepts
field_targets: [open_sso_channel.sys_channel]
sources: ["enrich:wiki-admin"]
---

sysChannel 指 SSO 平台侧系统渠道编码，落在 [[open_sso_channel.sys_channel]]；
SsoSystemDO.sysChannel 与 ssoSysChannel（DTO 字段）都是它的代码侧投影。
DB 实测形如 scpr-pplatform-pc，或带机构后缀 scpr-pplatform-pc_org{统一社会信用代码}。

## 需求背景

登录链路以 sysChannel 作为与 SSO 平台对话的系统标识：验证码策略查询 SsoSystemDO.captcha
（[[login_captcha_policy]]），租户配置回填 DTO 时也复用它。

## 版本演进

- v0（草稿）：术语边界来自代码赋值点与 DB 实测值。

边界：sysChannel 指 SSO 平台侧系统渠道编码；[[tenant_sso_chanel]]（tenant_setting_config.sso_tenant_chanel）
是租户配置的 SSO 统码，代码中常被直接赋给 DTO.ssoSysChannel（LocalTypeUserController.listUserPage 中
`byCode.getSsoTenantChanel()` → `setSsoSysChannel`），二者语义相邻但存储位置不同，不可互换。
另注意 [[org_code]] 是机构编码，不是渠道编码。

相关：[[open_sso_channel]]
