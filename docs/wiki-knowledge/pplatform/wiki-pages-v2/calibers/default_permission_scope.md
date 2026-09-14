---
type: caliber
title: 默认数据权限范围
page_key: default_permission_scope
domain: cust_org_permission
status: draft
aliases: [默认数据权限, SAME_AS_USER_ORG 兜底, 兜底口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: calibers
---

非管理员在查不到记录或类型为空时落到本口径：按 [[sys_cust_org_user_permission]].permission_type='SAME_AS_USER_ORG' 兜底，并用用户组织绑定回填 [[org_id_list]]。语义边界见 [[same_as_user_org]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 默认数据权限范围
predicate: "sys_cust_org_user_permission.permission_type = 'SAME_AS_USER_ORG'"
scope: 非管理员无记录/类型为空时的兜底
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType,listByCompany
```