---
type: caliber
title: 组织初始化企业范围口径
page_key: organization-init-company-scope
belong: calibers
domain: 客户角色与数据权限组织
status: published
aliases:
  - listBuildSuccessCusts
oid: 1
sources:
  - code_path
contract_version: "0.1"
field_targets: [cust_company_info.cust_build_status, cust_company_info.enable]
scope:
  databases: [lowcode_pplatform]
---

该口径描述仅选取建档成功企业初始化组织架构。

## 需求背景

用于组织批量初始化时筛选企业，避免对未认证或异常状态企业初始化组织。

## 版本演进

初始语义抽取版本，后续需补充与角色类型筛选的组合逻辑。

```ground:caliber
name: 组织初始化企业范围
predicate: cust_company_info.enable = 'Y' AND cust_company_info.cust_build_status = 'BUILD_SUCCESS'
scope: 仅建档成功企业初始化组织架构
evidence: code_path:CustSysOrgApplication.java:listBuildSuccessCusts()
```

相关页面：[[cust_company_info]] [[org-init-requires-build-success-and-role-type]]