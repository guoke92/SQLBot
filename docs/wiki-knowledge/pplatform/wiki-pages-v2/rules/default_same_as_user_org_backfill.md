---
type: rule
title: 无记录/空类型默认 SAME_AS_USER_ORG 并回填组织
page_key: default_same_as_user_org_backfill
domain: cust_org_permission
status: draft
aliases: [兜底回填组织, 默认 SAME_AS_USER_ORG 规则]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: rules
---

该规则把「查不到」变成「本人所属组织」而不是「全量可见」，是数据权限的安全兜底。回填来源是用户组织绑定，经 listCustUserOrgs 去重后写入 [[org_id_list]]；异常只告警不抛出，因此回填失败不会中断查询。语义边界见 [[same_as_user_org]]，口径见 [[default_permission_scope]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 无记录/空类型默认 SAME_AS_USER_ORG 并回填组织
content: 非管理员且未查出记录或 permissionType 为空时置 SAME_AS_USER_ORG，再由该用户在该企业+角色下的组织绑定填充 orgIdList（异常仅告警不抛出）。
impact: 数据范围兜底为『本人所属组织』，避免默认全量可见。
field_targets:
  - sys_cust_org_user_permission.permission_type
  - sys_cust_org_user_permission.org_id_list
evidence: code_path:DataPermissionApplication.java:fillOrgIdsIfSameAsUserOrg
```