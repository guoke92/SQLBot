---
type: caliber
title: 指定组织权限范围
page_key: specified_permission_scope
domain: cust_org_permission
status: draft
aliases: [指定组织权限, SPECIFIED 口径, 指定范围]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: calibers
---

本口径把 [[sys_cust_org_user_permission]].permission_type='SPECIFIED' 与「组织列表必须非空」绑定，构成保存时的硬校验，见 [[specified_requires_org_list]] 与 [[org_id_list]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 指定组织权限范围
predicate: "sys_cust_org_user_permission.permission_type = 'SPECIFIED'"
scope: 保存时强制校验 orgIdList 非空
evidence: code_path:DataPermissionApplication.java:saveDataPermission
```