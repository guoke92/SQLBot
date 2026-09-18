---
type: concept
title: 项目是否生产数据
page_key: project_is_prd
belong: concepts
domain: tenant
status: draft
aliases: [生产数据标签, 是否为生产数据]
maps_to: tenant_project.is_prd
field_targets: [tenant_project.is_prd]
sources: ['code_path:TenantProjectDomainService.java:367', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project]
also_confused_with: [wechat_prd_term, project_config_model]
adjudication: boundary
---

# 项目是否生产数据

document_claim:生产数据标签.md#23：项目维度「是否为生产数据」。catalog 注释同名，列 is_prd。
同步时 test_data 取反。不是企微立项单 prd（是否投产）。Y/N 不编字典页。

## 页面链接

- [[tables/tenant_project]]
- [[dicts/tenant_project__is_prd]]
- [[concepts/project_config_model]]
- [[concepts/wechat_prd_term]]
