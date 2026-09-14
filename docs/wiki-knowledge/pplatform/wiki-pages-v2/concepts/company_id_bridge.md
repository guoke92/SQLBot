---
type: concept
title: companyId / custId → 企业主键（cust_company_info.id）
page_key: company_id_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - companyId
  - custId
  - cust_id
  - custCompanyId
  - 企业主键
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.id]
  - semantic:field_semantics[cust_person_info.cust_company_id]
  - semantic:field_semantics[cust_group_rel.cust_id / parent_cust_id / root_cust_id]
contract_version: "0.1"
maps_to:
  - term: companyId
    target: cust_company_info.id
    evidence: code
  - term: custId
    target: cust_company_info.id
    evidence: code
  - term: cust_company_id
    target: cust_company_info.id
    evidence: code
  - term: cust_id
    target: cust_company_info.id
    evidence: code
field_targets:
  - cust_company_info.id
  - cust_person_info.cust_company_id
  - cust_group_rel.cust_id
  - cust_group_rel.parent_cust_id
  - cust_group_rel.root_cust_id
also_confused_with:
  - cust_company_info.code
belong: concepts
---

对外 Provider 暴露的 companyId / custId 与库内的 cust_company_id、cust_id 指向同一实体主键，即 [[tables/cust_company_info]].id。

## 需求背景

跨服务传参时同一个企业会以 companyId、custId、cust_company_id 三种写法出现；与之极易混淆的是业务编码 code，后者才是各关系表 ref_cust_company_info 系列列的关联键（见 [[concepts/company_code_bridge]]）。集团树中的 cust_id / parent_cust_id / root_cust_id 同样指向企业主键。

## 版本演进

v0：首次成页；仅登记有证据的术语映射，未对未出现的别名做外推。