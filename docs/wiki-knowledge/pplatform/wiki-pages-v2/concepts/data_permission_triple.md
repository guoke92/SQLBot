---
type: concept
title: 数据权限三维（user_id + company_id + company_type）
page_key: data_permission_triple
domain: 数据权限与组织
status: draft
aliases: [数据权限三维, user_id, company_id, company_type]
oid: 1
scope:
  databases: [base]
sources: [code, "enrich:wiki-admin"]
contract_version: "0.1"
maps_to:
  - sys_cust_org_user_permission.user_id
  - sys_cust_org_user_permission.company_id
  - sys_cust_org_user_permission.company_type
field_targets:
  - table: sys_cust_org_user_permission
    field: user_id
    meaning: 数据权限主体用户ID（与 company_id、company_type 构成唯一三维）
    evidence: code
  - table: sys_cust_org_user_permission
    field: company_id
    meaning: 数据权限归属企业ID
    evidence: code
  - table: sys_cust_org_user_permission
    field: company_type
    meaning: 数据权限归属企业角色类型
    evidence: code
  - table: sys_cust_org_user_permission
    field: permission_type
    meaning: 数据权限类型：ALL / SPECIFIED / SAME_AS_USER_ORG；无记录或为空时按 SAME_AS_USER_ORG 处理
    evidence: code
adjudication: 数据权限的唯一主体是「用户 + 企业 + 企业角色类型」三元组；同一用户在不同企业或不同角色下是独立的权限行，缺任一维度都会串权。
also_confused_with: [cust_person_info.company_type, cust_company_info.cust_company_type, org_id_list]
belong: concepts
---

术语桥：数据权限不是二维的「用户–企业」，而是三元组：user_id + company_id + company_type，三者共同构成唯一键。这意味着同一用户在同一企业但不同角色下可以拥有互相独立的数据权限行；读取权限时必须三个维度齐全。

company_type 与 [[concepts/company_role_type]] 同域（同名同义），不要和 [[tables/cust_person_info]].user_type（accountAdmin/accountNormal/accountGuest）混淆——后者是用户身份，前者是企业角色。三元组缺行或缺 permission_type 时的缺省行为见 [[rules/data_permission_default_same_as_user_org]]。

相关：[[sys_cust_org_user_permission]]
