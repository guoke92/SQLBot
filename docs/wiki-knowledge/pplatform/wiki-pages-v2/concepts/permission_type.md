---
type: concept
title: permissionType（数据权限类型）
page_key: permission_type
domain: cust_org_permission
status: draft
aliases: [permission_type, ALL, SPECIFIED, SAME_AS_USER_ORG, PERMISSION_ALL, PERMISSION_SPECIFIED, PERMISSION_SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication
contract_version: "0.1"
maps_to: sys_cust_org_user_permission.permission_type
field_targets: [sys_cust_org_user_permission.permission_type, sys_cust_org_user_permission.org_id_list]
adjudication: boundary
also_confused_with:
  - UserTypeEnum（accountAdmin/accountNormal/accountGuest；Java 名 admin/operator/guest）
  - 菜单权限 code
  - UserInfoFacade.ROLE_CODE_*
belong: concepts
---

permission_type 描述「数据可见范围」，userType 描述「用户在企业中的身份」，菜单/角色权限（code、ROLE_CODE_*）又是另一套，三者不可互换。DataPermissionApplication 注释明确只支持 ALL、SPECIFIED、SAME_AS_USER_ORG，不做 SAME_AS_ORG 映射。取值域与流转见 [[data_permission_permission_type]]，落库见 [[sys_cust_org_user_permission]]，身份维度见 [[admin]]，兜底语义见 [[same_as_user_org]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。