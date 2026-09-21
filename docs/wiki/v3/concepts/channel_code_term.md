---
type: concept
title: 渠道码
page_key: channel_code_term
belong: concepts
domain: tenant
status: draft
aliases: [项目渠道码, QD码, 项目码, 项目专属服务码]
maps_to: tenant_project.channel_code
field_targets: [tenant_project.channel_code]
sources: ['code_path:TenantProjectDaoImpl.java:93', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
also_confused_with: [project_code_input, tenant_flg_en, open_sso_channel_term, channel_archive_longteng,
  tenant_code_vs_db_tenant]
adjudication: boundary
---

# 渠道码

document_claim:渠道码.md#11：项目同步时生成的邀请注册标识码。catalog 注释「渠道码」。
document_claim:项目码.md：业务口「项目码」即本列 channel_code（主档），不是 tenant_project.project_code（项目编码）。
按 channel_code 查项目。不是客户录入的项目码记录，也不是 tenant_flg_en。
不是 open_sso_channel.channel_code（OpenAPI/SSO 渠道如 longteng），也不是 cust_company_info.channel_code / cust_access_secret.channel。
cust_project_rel.channel_code 是项目关联上的渠道码拷贝，仍不是 SSO 渠道主数据。

## 页面链接

- [[tables/tenant_project]]
- [[concepts/channel_archive_longteng]]
- [[concepts/open_sso_channel_term]]
- [[concepts/project_code_input]]
- [[concepts/tenant_code_vs_db_tenant]]
- [[concepts/tenant_flg_en]]
