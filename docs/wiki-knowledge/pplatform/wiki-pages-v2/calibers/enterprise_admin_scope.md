---
type: caliber
title: 企业管理员判定范围
page_key: enterprise_admin_scope
domain: cust_org_permission
status: draft
aliases: [企业管理员判定, user_type=admin, 管理员口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: calibers
---

本口径回答「谁是管理员」：只看 [[cust_person_info]].user_type='accountAdmin'，并叠加以启用与手机号等值匹配为条件的实际判定实现（见 [[admin]]、[[data_permission_save_admin_only]]、[[enabled_contact_scope]]）。它是数据权限编辑准入与管理员固定 ALL（[[enterprise_admin_fixed_all]]）共同依赖的过滤条件。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 企业管理员判定范围
predicate: "cust_person_info.user_type = 'accountAdmin'"
scope: 数据权限编辑准入、管理员固定 ALL 判定
evidence: code_path:DataPermissionApplication.java:assertCurrentUserIsAdminOfTargetCompany,isEnterpriseAdmin
```