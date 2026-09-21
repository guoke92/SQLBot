---
type: concept
title: 租户直推接入模式
page_key: direct_init_access_mode
belong: concepts
domain: cust
status: draft
aliases: [DIRECT_INIT, 方案2直推, 接入模式]
maps_to: tenant_setting_config.access_mode
field_targets: [tenant_setting_config.access_mode]
sources: ['code_path:DirectInitAccessModes.java:10', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [default_push_project, channel_code_term, direct_init_change_record]
adjudication: boundary
---

# 租户直推接入模式

空或 STANDARD=现网；DIRECT_INIT=方案2直推（V1.36 access_mode 列）。
DirectInitAccessModeGuard 按企业 db_tenant_code 读租户 access_mode 放行直推 OpenAPI。
全量保存租户配置时前端不传 accessMode，后端 preserveAccessModeIfBlank 禁止刷空 DIRECT_INIT。
同码 DIRECT_INIT 也会写到 cust_change_record.oper_channel，但是变更单通道标签，不是本列。
STANDARD 在本列=现网；与审批 project_type/flow_code 的 STANDARD（标准项目/流程）不是同一业务。

## 页面链接

- [[tables/tenant_setting_config]]
- [[dicts/tenant_setting_config__access_mode]]
- [[concepts/channel_code_term]]
- [[concepts/default_push_project]]
- [[concepts/direct_init_change_record]]
