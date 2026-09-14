---
type: concept
title: 企业角色
page_key: company_role
domain: 客户角色与端口
status: draft
aliases:
  - 客户角色
  - companyType
  - roleType
  - company_type_code
  - role_type
oid: 1
scope:
  databases:
    - db
sources:
  - db_dist:cust_role_info.role_type
  - db_dist:platform_product_cust_role.company_type_code
contract_version: "0.1"
maps_to:
  - cust_role_info.role_type
  - platform_product_cust_role.company_type_code
also_confused_with:
  - cust_company_info.cust_company_type
  - cust_person_info.company_type
adjudication: boundary
boundary: "cust_role_info.role_type 是客户与产品的角色关联，单个角色值；cust_company_info.cust_company_type 是企业主数据上的角色列表（JSON 数组）；cust_person_info.company_type 是联系人所属角色。"
belong: concepts
---

“企业角色”是本主题的核心术语，在客户角色语境中对应 [[cust_role_info]].role_type，在产品端口配置语境中对应 [[platform_product_cust_role]].company_type_code，两者共用编码值域（CORE、SUPPLIER、FINANCE 等）。

## 需求背景

同义词链（客户角色 / companyType / roleType / company_type_code / role_type）在代码与库表中混用，需要通过边界判定区分三处易混字段。角色在全量覆盖写入时以 JSON 数组形式传入并按单个值落库，见 [[role_full_overwrite]]；下游同步时会从 roleClass 中解析出 companyType，见 [[role_downstream_sync]]。

## 版本演进

- v0（draft）：依据 term_bridges 与 relation_audit（platform_product_cust_role.company_type_code ↔ cust_role_info.role_type 为 derived 逻辑关联）首次成页。