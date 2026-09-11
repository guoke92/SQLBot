---
type: concept
title: ref_cust_company_info → 企业业务编码（cust_company_info.code）
page_key: concept.company_code_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - ref_cust_company_info
  - 企业业务编码
  - cust_company_code
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.code]
  - semantic:field_semantics[cust_person_info.ref_cust_company_info]
  - semantic:field_semantics[cust_role_info.ref_cust_company_info]
  - semantic:field_semantics[cust_project_rel.ref_cust_project_rel_cust_company_info]
contract_version: "0.1"
maps_to:
  - term: ref_cust_company_info
    target: cust_company_info.code
    evidence: code
  - term: ref_cust_project_rel_cust_company_info
    target: cust_company_info.code
    evidence: code
field_targets:
  - cust_company_info.code
  - cust_person_info.ref_cust_company_info
  - cust_role_info.ref_cust_company_info
  - cust_project_rel.ref_cust_project_rel_cust_company_info
also_confused_with:
  - cust_company_info.id
---

各关系表中以 ref_cust_company_info（或带前缀的变体）命名的列，关联的不是企业主键而是业务编码，即 [[tables/cust_company_info]].code。

## 需求背景

该编码在新建企业时由 DataModelUtils.uuid() 生成，是关系表拼接的稳定锚点；联系人查询的主关联键即 ref_cust_company_info。做 join 时若误用 id 关联会漏数据。

## 版本演进

v0：首次成页。