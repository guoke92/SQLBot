---
type: rule
title: 数据权限缺省按 SAME_AS_USER_ORG 处理
page_key: data_permission_default_same_as_user_org
domain: 数据权限与组织
status: draft
aliases: [数据权限缺省规则, 无记录默认同用户组织]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
belong: rules
---

当 [[tables/sys_cust_org_user_permission]] 中没有对应三元组的记录，或查出的 permission_type 为空时，系统不报错也不放行全量，而是按 SAME_AS_USER_ORG（同用户所属组织）处理。这是一条「空值即缺省」的隐式流转，见 [[processes/data_permission_type_fsm]]。

需要与企业管理员的处理区分：如果主体是该企业该角色启用中的管理员，则直接按 ALL（见 [[calibers/company_admin]]），而不是缺省值。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义「无记录或为空时按 SAME_AS_USER_ORG 处理」及 DataPermissionApplication 证据得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 数据权限缺省
statement: 无权限记录或 permission_type 为空时按 SAME_AS_USER_ORG 处理，非管理员不放行为全部数据
condition: 查询权限且主体不是该企业该角色启用中的管理员
action: 以用户所属组织作为数据范围
evidence: code_path:DataPermissionApplication.java#getByUserCompanyType / #listByCompany
```