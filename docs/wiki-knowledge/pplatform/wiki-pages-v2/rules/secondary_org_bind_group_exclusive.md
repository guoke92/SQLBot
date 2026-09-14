---
type: rule
title: 二级组织绑定不得跨（企业, 角色）分组
page_key: secondary_org_bind_group_exclusive
domain: cust_org_permission
status: draft
aliases: [二级组织唯一归属, 用户绑定分组校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
belong: rules
---

该规则保证组织归属唯一、且不落空分组。分组维度是 (custId, companyType)，与 [[company_type]]、[[cust_id_company_id]] 的语义一致；绑定的用户有效性另由 [[bind_org_user_requires_enabled_contact]] 把关。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 二级组织绑定不得跨（企业, 角色）分组
content: Sheet1 中同一 orgId 只能属于一个 (custId, companyType) 分组，且每组在 Sheet2 中必须至少有一行用户绑定。
impact: 保证组织归属唯一、避免空分组落库。
field_targets: []
evidence: code_path:CustSysOrgApplication.java:importSecondaryOrgUserBind
```