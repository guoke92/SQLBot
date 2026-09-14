---
type: caliber
title: 建档成功企业范围
page_key: build_success_cust_scope
domain: cust_org_permission
status: draft
aliases: [建档成功企业, BUILD_SUCCESS 范围, 建档准入口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
belong: calibers
---

本口径以 [[cust_company_info]].cust_build_status='BUILD_SUCCESS' 圈定可做组织动作的企业集合，是 [[org_operate_requires_build_success]] 的判定基础。状态流转见 [[cust_build_status]]。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 建档成功企业范围
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS'"
scope: 初始化根组织、加/改组织的准入条件
evidence: code_path:CustSysOrgApplication.java:checkCustBuildStatus,listBuildSuccessCusts
```