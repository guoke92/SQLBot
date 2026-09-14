---
type: concept
title: 管理员
page_key: admin
domain: cust_org_permission
status: draft
aliases: [admin, 企业管理员, 平台管理员]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
maps_to: cust_person_info.user_type
field_targets: [cust_person_info.user_type, cust_person_info.enable, cust_person_info.phone]
adjudication: boundary
also_confused_with:
  - 需求文档中的平台管理员（跨企业）
belong: concepts
---

代码中可判定的只有企业内管理员：[[cust_person_info]].user_type='accountAdmin' 且 enable='Y'，且 phone 与登录用户名密文一致。数据权限保存额外要求 companyId 必须等于当前登录企业，即无法跨企业代理配置（[[data_permission_save_admin_only]]）。需求文档中的「平台管理员」是跨企业概念，与代码可判定范围不同，不可据其推断权限行为。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。