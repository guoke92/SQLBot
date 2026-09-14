---
type: rule
title: 企业管理员数据权限固定 ALL
page_key: enterprise_admin_fixed_all
domain: cust_org_permission
status: draft
aliases: [管理员固定 ALL, 管理员不读权限库]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: rules
---

管理员不受组织范围限制，且无需预先配置权限记录——这是查询链路的短路分支，先判 [[enterprise_admin_scope]] 再决定是否读 [[sys_cust_org_user_permission]]。对应口径 [[admin_permission_scope]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 企业管理员数据权限固定 ALL
content: getByUserCompanyType 先判 isEnterpriseAdmin，命中则直接构造 permissionType=ALL、orgIdList=null 返回，不读权限库。
impact: 管理员不受组织范围限制，且无需预先配置权限记录。
field_targets:
  - sys_cust_org_user_permission.permission_type
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType,isEnterpriseAdmin
```