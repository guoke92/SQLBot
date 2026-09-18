---
type: concept
title: 企业项目关联状态
page_key: project_rel_status
belong: concepts
domain: cust
status: draft
aliases: [关联状态, 关联已生效, 供应商关联项目即生效, 企业关联项目配置]
maps_to: cust_project_rel.status
field_targets: [cust_project_rel.status]
sources: ['code_path:CustSyncEventProcessor.java:3128', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_project_rel]
also_confused_with: [default_push_project, project_code_input]
adjudication: boundary
---

# 企业项目关联状态

document_claim:关联状态.md#17 / 供应商关联项目即生效.md#28。catalog 注释「关联状态」。
供应商+融易单/订单融资写入 1；其它写入 0。运营确认接口写成 Y。不要把 0/1 和 Y 当成两套业务口径硬套。

## 页面链接

- [[tables/cust_project_rel]]
- [[dicts/cust_project_rel__status]]
- [[concepts/default_push_project]]
- [[concepts/project_code_input]]
