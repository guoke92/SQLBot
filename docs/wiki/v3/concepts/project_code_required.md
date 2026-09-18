---
type: concept
title: 项目码是否必填
page_key: project_code_required
belong: concepts
domain: tenant
status: draft
aliases: [项目专属服务码必填, 自主注册项目码]
maps_to: tenant_setting_config.project_code_required
field_targets: [tenant_setting_config.project_code_required, tenant_setting_config.default_project_id]
sources: ['code_path:TenantDomainService.java:234', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_setting_config]
also_confused_with: [default_push_project, self_reg_flag]
adjudication: boundary
---

# 项目码是否必填

租户运营配置字段，不是客户录入的 cust_project_code_record。
现网 Y 时必须已配 default_project_id；document_claim:租户运营配置-项目码必填.md 文案与代码相反，以 TenantDomainService 为准。

## 页面链接

- [[tables/tenant_setting_config]]
- [[dicts/tenant_setting_config__project_code_required]]
- [[concepts/default_push_project]]
- [[concepts/self_reg_flag]]
