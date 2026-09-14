---
type: rule
title: 组织操作前置：企业建档成功
page_key: org_operate_requires_build_success
domain: cust_org_permission
status: draft
aliases: [组织操作前置, 建档成功门槛]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
belong: rules
---

未认证企业无法创建或初始化组织。该规则同时出现在单企业动作（addSubOrg、initRootOrg）与批量扫描两个入口，口径见 [[build_success_cust_scope]] 与 [[enabled_cust_scope]]，状态见 [[cust_build_status]]。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:rule
name: 组织操作前置：企业建档成功
content: addSubOrg 调用 checkCustBuildStatus 校验 cust_build_status=BUILD_SUCCESS；initRootOrg 同样要求建档成功；批量初始化按 enable='Y' + BUILD_SUCCESS 翻页扫描。
impact: 未认证企业无法创建/初始化组织。
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.enable
evidence: code_path:CustSysOrgApplication.java:checkCustBuildStatus,listBuildSuccessCusts
```