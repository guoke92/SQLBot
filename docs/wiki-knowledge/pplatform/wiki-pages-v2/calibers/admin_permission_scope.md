---
type: caliber
title: 管理员数据权限范围
page_key: admin_permission_scope
domain: cust_org_permission
status: draft
aliases: [管理员数据权限, ALL 口径, 管理员全量范围]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: calibers
---

本口径指管理员查询时固定返回的 permission_type='ALL'，不读权限库，见 [[enterprise_admin_fixed_all]] 与 [[admin]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 管理员数据权限范围
predicate: "sys_cust_org_user_permission.permission_type = 'ALL'"
scope: 企业管理员查询固定返回值（不读库）
evidence: code_path:DataPermissionApplication.java:getByUserCompanyType
```