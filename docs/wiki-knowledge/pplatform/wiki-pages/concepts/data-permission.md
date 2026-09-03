---
type: concept
title: 数据权限
page_key: data-permission
domain: 客户角色与数据权限组织
status: published
aliases:
  - 数据范围
  - 数据权限类型
  - permissionType
oid: 1
sources:
  - code
contract_version: "0.1"
maps_to: sys_cust_org_user_permission.permission_type
field_targets:
  - sys_cust_org_user_permission.permission_type
adjudication: boundary
also_confused_with:
  - 菜单权限
  - 功能权限
  - 角色权限
scope:
  databases: [lowcode_pplatform]
---

数据权限控制用户可见组织数据范围，取值 ALL/SPECIFIED/SAME_AS_USER_ORG。

## 需求背景

需要区分数据权限与菜单/功能权限：数据权限控制数据范围，菜单权限控制功能入口，两者均通过用户角色体系管理但维度不同。

## 版本演进

初始语义抽取版本，后续需补充数据权限与组织树联动规则。

相关页面：[[sys_cust_org_user_permission]] [[default-data-permission]]