---
type: concept
title: 企业角色类型同域（cust_company_type / company_type / role_type）
page_key: company_role_type
domain: 数据权限与组织
status: draft
aliases: [企业角色类型, cust_company_type, company_type, role_type]
oid: 1
scope:
  databases: [base]
sources: [code, "enrich:wiki-admin"]
contract_version: "0.1"
maps_to:
  - cust_company_info.cust_company_type
  - cust_person_info.company_type
  - cust_role_info.role_type
  - sys_cust_org_user_permission.company_type
field_targets:
  - table: cust_company_info
    field: cust_company_type
    meaning: 企业角色类型，JSON 数组字符串（如 ["SUPPLIER"]），可多角色
    evidence: code
  - table: cust_person_info
    field: company_type
    meaning: 该联系人归属的企业角色类型（与 cust_company_info.cust_company_type 对应）
    evidence: code
  - table: cust_role_info
    field: role_type
    meaning: 企业角色类型（与 cust_company_info.cust_company_type 同域；initRootOrg 按此字段逐角色初始化根组织）
    evidence: code
  - table: sys_cust_org_user_permission
    field: company_type
    meaning: 数据权限归属企业角色类型
    evidence: code
adjudication: 同一语义（企业角色）在四张表上字段名不同：企业侧是 JSON 数组字符串（多角色，判定用"包含"），角色表是按角色拆行，联系人与数据权限表是单值；跨表比较时必须先做展开/对齐。
also_confused_with: [user_type, identify_style]
belong: concepts
---

术语桥：「企业角色类型」在四张表上以四个不同字段名出现——cust_company_info.cust_company_type、cust_person_info.company_type、cust_role_info.role_type、sys_cust_org_user_permission.company_type。语义分析明确后三者与 cust_company_type 同域。

关键差异是形态而非语义：企业主数据上是 JSON 数组字符串（如 ["SUPPLIER"]，可多角色，判定用「包含」，见 [[calibers/platform_operator_company]]），cust_role_info 则按角色逐行拆分（initRootOrg 按此逐角色初始化根组织），联系人与数据权限表是单值。跨表比较前必须先展开成集合再对齐，否则多角色企业会漏判。适用场景见 [[concepts/data_permission_triple]]。

相关：[[cust_company_info]]
