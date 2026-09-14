---
type: concept
title: SAME_AS_USER_ORG
page_key: same_as_user_org
domain: cust_org_permission
status: draft
aliases: [SAME_AS_USER_ORG]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
maps_to: permission_type.SAME_AS_USER_ORG
field_targets: [sys_cust_org_user_permission.permission_type, sys_cust_org_user_permission.org_id_list]
adjudication: boundary
also_confused_with:
  - SAME_AS_ORG
belong: concepts
sources: ["enrich:wiki-admin"]
---

saveDataPermission 注释明确「不做 SAME_AS_ORG 映射」；查询/列表遇到空类型才回填本值，且回填的 [[org_id_list]] 是用户组织绑定而非角色默认组织。它是兜底而非用户可选配置的等价物，见 [[default_permission_scope]] 与 [[data_permission_permission_type]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

相关：[[sys_cust_org_user_permission]]
