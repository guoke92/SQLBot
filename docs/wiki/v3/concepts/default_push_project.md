---
type: concept
title: 默认关联项目
page_key: default_push_project
belong: concepts
domain: cust
status: draft
aliases: [默认推送项目, 未填项目码自动关联]
maps_to: cust_project_pushcust.project_id
field_targets: [cust_project_pushcust.project_id]
sources: ['code_path:CustSyncEventProcessor.java:3106', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_project_pushcust]
also_confused_with: [project_code_input, project_code_required, project_rel_status]
adjudication: boundary
---

# 默认关联项目

需求「默认关联项目」是租户/渠道配置。现网 cust_project_pushcust 按 SSO 渠道取 project_id，再转 Long 查 tenant_project。
不是客户自己录入的项目码记录。也不是 tenant_setting_config.default_project_id（项目码必填时的租户默认项目）。
document_claim:默认关联项目.md

## 页面链接

- [[tables/cust_project_pushcust]]
- [[concepts/project_code_input]]
- [[concepts/project_code_required]]
- [[concepts/project_rel_status]]
