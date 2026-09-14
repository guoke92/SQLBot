---
type: caliber
title: 有效企业范围
page_key: enabled_cust_scope
domain: cust_org_permission
status: draft
aliases: [有效企业, enable=Y 企业, 企业启用口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
contract_version: "0.1"
belong: calibers
---

本口径以 [[cust_company_info]].enable='Y' 标识企业是否有效。它与建档成功条件是并列的两把尺子：组织初始化批处理通常要求二者同时成立（[[build_success_cust_scope]]），用户绑定查企业也走本口径。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 有效企业范围
predicate: "cust_company_info.enable = 'Y'"
scope: 组织初始化批处理、用户绑定查企业
evidence: code_path:CustSysOrgApplication.java:listBuildSuccessCusts
```