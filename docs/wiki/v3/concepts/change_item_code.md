---
type: concept
title: 变更项编码
page_key: change_item_code
belong: concepts
domain: cust
status: draft
aliases: [变更项, UN0001, UN0009]
maps_to: cust_change_cfg.item_code
field_targets: [cust_change_cfg.item_code]
sources: ['code_path:CustUpdateItemCodeConstants.java:8', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_change_cfg]
also_confused_with: [add_company_role_change]
adjudication: boundary
---

# 变更项编码

变更项中文来自 CustUpdateItemCodeConstants 注释，配置行在 cust_change_cfg。
变更单 alter_type_id 存的是逗号分隔的 cfg.id，不是 item_code，不要当成 EQUI_JOIN。
「增加企业角色」钉 UN0009，不要用整列 item_code 当唯一过滤。

## 页面链接

- [[tables/cust_change_cfg]]
- [[dicts/cust_change_cfg__item_code]]
- [[concepts/add_company_role_change]]
