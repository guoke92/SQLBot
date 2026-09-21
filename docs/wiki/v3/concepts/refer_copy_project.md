---
type: concept
title: 跨贴牌项目引用
page_key: refer_copy_project
belong: concepts
domain: tenant
status: draft
aliases: [复制的租户项目, 跨贴牌复制]
maps_to: tenant_project.refer_tenant_project_id
field_targets: [tenant_project.refer_tenant_project_id]
sources: ['code_path:ProjectClientSyncService.java:64', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/项目上线审批流程.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
also_confused_with: [tenant_project_code_join]
adjudication: boundary
---

# 跨贴牌项目引用

document_claim:跨贴牌项目引用.md#15：配置新项目时引用其他贴牌项目。catalog 注释「复制的租户项目」。
ProjectClientSyncService 只 set 该列，代码未对 tenant_project.id 做 EQUI_JOIN。不要当成审批关联编码。

## 页面链接

- [[tables/tenant_project]]
- [[concepts/tenant_project_code_join]]
