---
type: rule
title: 数据权限仅本企业管理员可保存
page_key: data_permission_save_admin_only
domain: cust_org_permission
status: draft
aliases: [数据权限保存准入, 本企业管理员校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: rules
---

保存/批量保存数据权限前先做三重校验：企业一致、角色一致、人合法。它决定了业务侧无法替其它企业配置权限，也决定 [[enterprise_admin_scope]] 与 [[enabled_contact_scope]] 是保存链路的必经过滤。落库对象见 [[sys_cust_org_user_permission]]，身份语义见 [[admin]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 数据权限仅本企业管理员可保存
content: 保存/批量保存前校验：companyId 必须等于当前登录企业、companyType 与当前登录角色一致、当前用户为 cust_person_info.user_type='accountAdmin' 且 enable='Y' 且 phone 匹配登录用户名密文。
impact: 越权配置数据权限被拒绝；业务侧无法替其它企业配置。
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.phone
  - sys_cust_org_user_permission.company_id
evidence: code_path:DataPermissionApplication.java:assertCurrentUserIsAdminOfTargetCompany
```