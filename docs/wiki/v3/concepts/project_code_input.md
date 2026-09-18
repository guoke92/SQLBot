---
type: concept
title: 录入项目码
page_key: project_code_input
belong: concepts
domain: cust
status: draft
aliases: [项目码记录, 项目专属服务码]
maps_to: cust_project_code_record.company_id
field_targets: [cust_project_code_record.company_id, cust_project_code_record.channel_code]
sources: ['code_path:CustProjectRelEnhanceService.java:364', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_project_code_record]
also_confused_with: [default_push_project, channel_code_term, project_rel_status]
adjudication: boundary
---

# 录入项目码

客户在认证过程中录入项目码，落在 cust_project_code_record.company_id=企业主键。
不要和租户配置的默认关联项目表搞混，也不要和项目 channel_code（渠道码）搞混。

## 页面链接

- [[tables/cust_project_code_record]]
- [[concepts/channel_code_term]]
- [[concepts/default_push_project]]
- [[concepts/project_rel_status]]
