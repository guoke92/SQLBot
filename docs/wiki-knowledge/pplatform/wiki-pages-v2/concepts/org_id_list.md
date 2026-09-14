---
type: concept
title: orgIdList
page_key: org_id_list
domain: cust_org_permission
status: draft
aliases: [orgIds, org_id_list]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
maps_to: sys_cust_org_user_permission.org_id_list
field_targets: [sys_cust_org_user_permission.org_id_list, sys_cust_org_user_permission.permission_type]
adjudication: synonym
also_confused_with:
  - PlatCustOrgDTO.orgId
belong: concepts
sources: ["enrich:wiki-admin"]
---

orgIdList / orgIds / org_id_list 都是 sys_cust_org 的 id 集合，属客户组织架构一路（见 [[org]]）。SAME_AS_USER_ORG 回填时经 listCustUserOrgs 得到并按 orgId 去重，来源是用户组织绑定而不是角色默认组织，见 [[same_as_user_org]]；SPECIFIED 下该字段非空是保存硬条件（[[specified_requires_org_list]]）。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

相关：[[sys_cust_org_user_permission]]
