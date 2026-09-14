---
type: process
title: 数据权限类型（permission_type）
page_key: data_permission_permission_type
domain: cust_org_permission
status: draft
aliases: [数据权限类型, permission_type, ALL, SPECIFIED, SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: processes
---

数据权限类型是枚举式字符串常量的取值域，落在 [[sys_cust_org_user_permission]].permission_type 上。它描述「能看到多少组织」，与用户身份（user_type）不是一回事，边界见 [[permission_type]]。

保存路径不产生状态跃迁：传入什么类型就写什么类型，SPECIFIED 另加组织列表非空校验（[[specified_requires_org_list]]）。查询路径则存在两处隐式赋值：管理员固定 ALL（[[enterprise_admin_fixed_all]]），非管理员无记录或类型为空时兜底 SAME_AS_USER_ORG 并回填组织（[[default_same_as_user_org_backfill]]）。相关口径见 [[admin_permission_scope]]、[[specified_permission_scope]]、[[default_permission_scope]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:process
name: 数据权限类型
field: sys_cust_org_user_permission.permission_type
states:
  - value: ALL
    label: 全部数据（管理员固定）
    source: code_const
  - value: SPECIFIED
    label: 指定组织范围
    source: code_const
  - value: SAME_AS_USER_ORG
    label: 与用户组织绑定一致（默认兜底）
    source: code_const
transitions:
  - from: ALL
    event: 保存/批量保存并传入 permissionType
    to: ALL
    evidence: code_path:DataPermissionApplication.java:saveDataPermission
  - from: SPECIFIED
    event: 保存且 orgIdList 非空
    to: SPECIFIED
    evidence: code_path:DataPermissionApplication.java:saveDataPermission
  - from: SPECIFIED
    event: 保存但 orgIdList 为空
    to: SPECIFIED
    evidence: code_path:DataPermissionApplication.java:saveDataPermission（抛 CommonException 中断）
  - from: ""
    event: 查询：无记录或 permissionType 为空（非管理员）
    to: SAME_AS_USER_ORG
    evidence: code_path:DataPermissionApplication.java:getByUserCompanyType
  - from: ALL
    event: 查询：判断为企业管理员（userType=admin 且 enable=Y）
    to: ALL
    evidence: code_path:DataPermissionApplication.java:isEnterpriseAdmin
```