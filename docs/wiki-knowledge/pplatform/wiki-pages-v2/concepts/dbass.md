---
type: concept
title: DBAss
page_key: dbass
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - dbass
  - DBaaS
  - DbassProvider
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:getTenantSetting
  - code:DbassProviderImpl
contract_version: "0.1"
maps_to: tenant_setting_config.dbass_app_id
also_confused_with:
  - open_sso_channel.app_id
adjudication: boundary
belong: concepts
field_targets: [tenant_setting_config.dbass_app_id]
sources: ["enrich:wiki-admin"]
---

（document_claim，未证实）文档主张存在通道初始化链路：
SsoSysChannelInitService.initDbassAndSsoConfig(configId) → DBAss 写 dbass appId →
PlatformTenantLineServiceImpl 同步平台线路 → PlatformComponentFacade 调 SSO 通道初始化。
该主张在给定语义分析中为 uncovered，仅作版本演进记录，不作为契约。

DBAss 在本主题中以租户侧接入凭据体现：[[tenant_setting_config.dbass_app_id]]（另有 dbass_private_key）。

## 需求背景

DBAss 能力（本主题中体现为营业执照 OCR / 行业查询）需要租户级接入凭据；
凭据返回前端前必须脱敏（dbassAppId 置 null）。

## 版本演进

- v0（草稿）：术语边界来自代码与脱敏点。
- （document_claim，未证实）initDbassAndSsoConfig / PlatformTenantLineServiceImpl / PlatformComponentFacade 初始化链路未见代码证据，待核实。

边界：本主题中 DbassProvider 实际提供营业执照 OCR（getCompanyIndustry/ocrBizLicense）能力，
与 SSO 渠道初始化并非同一套配置；tenant_setting_config 的 dbass_app_id/dbass_private_key
才是 DBAss 接入凭据，不可与 [[app_id]]（open_sso_channel.app_id）混用。

相关：[[tenant_setting_config]]
