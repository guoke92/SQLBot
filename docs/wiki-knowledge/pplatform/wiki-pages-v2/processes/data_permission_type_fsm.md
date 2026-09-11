---
type: process
title: 数据权限类型机（permission_type）
page_key: process.data_permission_type_fsm
domain: 数据权限与组织
status: draft
aliases: [数据权限类型机, permission_type, ALL, SPECIFIED, SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: sys_cust_org_user_permission.permission_type
---

数据权限类型机，承载于 [[tables/sys_cust_org_user_permission]].permission_type，取值为 ALL（全部数据）/ SPECIFIED（指定组织）/ SAME_AS_USER_ORG（同用户所属组织）。这是一张「按主体三维惰性推进」的状态机：无记录或值为空时按 SAME_AS_USER_ORG 处理（见 [[rules/data_permission_default_same_as_user_org]]）；一旦判定主体是该企业该角色启用中的管理员，则直接落到 ALL（判定口径见 [[calibers/company_admin]]）。

SPECIFIED 的保存要求 org_id_list 必填，见 [[rules/specified_requires_org_id_list]]；SAME_AS_USER_ORG 的组织范围由用户组织绑定回填。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 DataPermissionApplication。

## 版本演进

v0：依据 code 证据建模，含「空值即缺省」这一非显式落库的隐式流转。

```ground:process
name: 数据权限类型机
field: sys_cust_org_user_permission.permission_type
states:
  - value: ALL
    label: 全部数据
    source: code_enum
  - value: SPECIFIED
    label: 指定组织
    source: code_enum
  - value: SAME_AS_USER_ORG
    label: 同用户所属组织
    source: code_enum
transitions:
  - from: 空（无记录）
    event: 查询且非企业管理员
    to: SAME_AS_USER_ORG
    evidence: code_path:DataPermissionApplication.java#getByUserCompanyType
  - from: 空（permissionType 为空）
    event: 列表查询补默认值
    to: SAME_AS_USER_ORG
    evidence: code_path:DataPermissionApplication.java#listByCompany
  - from: 任意
    event: 用户为该企业该角色启用中的管理员
    to: ALL
    evidence: code_path:DataPermissionApplication.java#isEnterpriseAdmin
  - from: SAME_AS_USER_ORG
    event: 保存指定组织（orgIdList 必填）
    to: SPECIFIED
    evidence: code_path:DataPermissionApplication.java#saveDataPermission
  - from: SPECIFIED
    event: 保存为全部
    to: ALL
    evidence: code_path:DataPermissionApplication.java#saveDataPermissionBatch
```