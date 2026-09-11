---
type: table
title: 客户组织数据权限表 sys_cust_org_user_permission
page_key: table.sys_cust_org_user_permission
domain: 数据权限与组织
status: draft
aliases: [sys_cust_org_user_permission, 数据权限表]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

数据权限表，主体维度由 user_id + company_id + company_type 构成唯一三维，见 [[concepts/data_permission_triple]]。permission_type 的取值与流转见 [[processes/data_permission_type_fsm]]；缺省处理见 [[rules/data_permission_default_same_as_user_org]]；SPECIFIED 必填 org_id_list 见 [[rules/specified_requires_org_id_list]]。企业管理员在该企业该角色下的判定口径见 [[calibers/company_admin]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；结论来自代码侧 DataPermissionApplication 证据。

## 版本演进

v0：依据 code 证据建档。

