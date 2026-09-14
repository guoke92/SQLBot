---
type: caliber
title: 启用联系人范围
page_key: enabled_contact_scope
domain: cust_org_permission
status: draft
aliases: [启用联系人, enable=Y, 联系人有效口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
  - code:CustSysOrgApplication.java
contract_version: "0.1"
belong: calibers
---

本口径把 [[cust_person_info]].enable='Y' 作为联系人「有效」的门槛，供管理员/经办人查询与组织绑定校验复用。禁用联系人既不能被判为管理员，也不能被挂到组织下（见 [[bind_org_user_requires_enabled_contact]]）。

## 需求背景
本页仅依据代码证据（DataPermissionApplication、CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 启用联系人范围
predicate: "cust_person_info.enable = 'Y'"
scope: 管理员/经办人查询、组织绑定校验
evidence: code_path:DataPermissionApplication.java:isEnterpriseAdmin
```