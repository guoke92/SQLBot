---
type: rule
title: 组织导入一级组织名称必须等于企业名称
page_key: org_import_root_name_equals_company_name
domain: cust_org_permission
status: draft
aliases: [根组织名称校验, 一级组织名称一致]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
belong: rules
---

导入解析（checkExcelData）阶段即拦截，防止导入产生与主数据不一致的根组织。涉及 [[cust_company_info]].name 与该企业组织树的根行。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 组织导入一级组织名称必须等于企业名称
content: checkExcelData 中 parentOrgName='/' 的根行只能一条且 orgName 必须等于 cust_company_info.name，否则报错。
impact: 防止导入产生与主数据不一致的根组织。
field_targets:
  - cust_company_info.name
evidence: code_path:CustSysOrgApplication.java:checkExcelData
```