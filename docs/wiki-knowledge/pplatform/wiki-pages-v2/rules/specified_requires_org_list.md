---
type: rule
title: SPECIFIED 必须携带组织列表
page_key: specified_requires_org_list
domain: cust_org_permission
status: draft
aliases: [指定组织校验, SPECIFIED 非空校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: rules
---

该规则阻止「指定组织但范围为空」的悬空权限落库，是 [[specified_permission_scope]] 的强制实现。涉及 [[sys_cust_org_user_permission]] 的 permission_type 与 [[org_id_list]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: SPECIFIED 必须携带组织列表
content: permissionType=SPECIFIED 且 orgIdList 为空时抛 CommonException('指定组织时，请选择组织列表')。
impact: 阻止『指定组织但无范围』的悬空权限。
field_targets:
  - sys_cust_org_user_permission.permission_type
  - sys_cust_org_user_permission.org_id_list
evidence: code_path:DataPermissionApplication.java:saveDataPermission,saveDataPermissionBatch
```