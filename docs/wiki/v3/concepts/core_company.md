---
type: concept
title: 核心企业
page_key: core_company
belong: concepts
domain: cust
status: draft
aliases: [买方核心企业, 链主企业]
maps_to: cust_company_info.cust_company_type
field_targets: [cust_company_info.cust_company_type, cust_role_info.role_type]
sources: ['code_path:CustCompanyTypeEnum.java:18', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info, cust_role_info]
also_confused_with: [add_company_role_change, finance_org_type_term, group_member_rel]
adjudication: boundary
---

# 核心企业

角色码 CORE 来自 CustCompanyTypeEnum，落在 cust_company_type（JSON 数组）以及 cust_role_info.role_type。
问「核心企业」应过滤角色，而不是把 company_type 当成单值字典列硬套。
「增加企业角色」是变更项 UN0009，不是这列本身。金融机构类型是补充字段 finance_org_type。集团成员看 cust_group_rel。

## 页面链接

- [[tables/cust_company_info]]
- [[tables/cust_role_info]]
- [[dicts/cust_role_info__role_type]]
- [[concepts/add_company_role_change]]
- [[concepts/finance_org_type_term]]
- [[concepts/group_member_rel]]
