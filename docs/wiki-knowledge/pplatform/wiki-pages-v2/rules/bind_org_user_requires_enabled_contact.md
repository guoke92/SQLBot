---
type: rule
title: 绑定组织用户要求联系人在该企业角色下启用
page_key: bind_org_user_requires_enabled_contact
domain: cust_org_permission
status: draft
aliases: [绑定用户启用校验, 用户未加入该企业]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
belong: rules
---

禁用或未加入企业的用户不能被挂到组织下。计数条件同时覆盖用户、企业编码、角色与启用标记，说明 [[cust_person_info]] 的这三列构成绑定校验的最小键；相关口径见 [[enabled_contact_scope]]。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 绑定组织用户要求联系人在该企业角色下启用
content: 按 userId + refCustCompanyInfo + companyType + enable='Y' 计数，为 0 则报『用户未加入该企业或未启用』。
impact: 禁用/未加入企业的用户不能被挂到组织下。
field_targets:
  - cust_person_info.enable
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
evidence: code_path:CustSysOrgApplication.java:importSecondaryOrgUserBind
```