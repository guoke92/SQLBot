---
type: caliber
title: 租户隔离范围
page_key: tenant_isolation_scope
domain: cust_org_permission
status: draft
aliases: [租户隔离, db_tenant_code 口径, 租户过滤]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustSysOrgApplication.java
  - code:CustGroupRelApplication.java
contract_version: "0.1"
belong: calibers
---

本口径以 [[cust_company_info]].db_tenant_code = 入参租户为隔离键，作用于组织初始化、集团导入与运营方查询。运营方场景还叠加 test_data 过滤（见 [[cust_company_info]]）。

## 需求背景
本页仅依据代码证据（CustSysOrgApplication、CustGroupRelApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

```ground:caliber
name: 租户隔离范围
predicate: "cust_company_info.db_tenant_code = 入参租户"
scope: 组织初始化、集团导入、运营方查询
evidence: code_path:CustSysOrgApplication.java:listBuildSuccessCusts；CustGroupRelApplication.java:queryTenantOperatorCompany
```