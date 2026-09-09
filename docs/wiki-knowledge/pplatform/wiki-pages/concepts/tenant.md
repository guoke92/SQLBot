---
type: concept
title: 租户
page_key: tenant
belong: concepts
domain: 客户角色与数据权限组织
status: published
aliases:
  - dbTenantCode
  - tenantCode
oid: 1
sources:
  - db
  - code
contract_version: "0.1"
maps_to: cust_company_info.db_tenant_code / cust_role_info.db_tenant_code
field_targets:
  - cust_company_info.db_tenant_code
  - cust_role_info.db_tenant_code
adjudication: boundary
also_confused_with:
  - 逻辑租户 app_tenant_code
scope:
  databases: [lowcode_pplatform]
---

租户标识用于数据隔离，db_tenant_code 是数据租户标识，app_tenant_code 是逻辑租户标识。

## 需求背景

需求文档 3.3.2 要求租户维度隔离通过 db_tenant_code 区分。代码证据确认 CustRoleApplication.java:addRoleInfo() 中 MetaDataThreadLocalConfig.setDbTenantCode('all') 显式切换租户；DataPermissionApplication 使用 db_tenant_code 查询用户；业务查询语句使用 db_tenant_code 过滤。

## 版本演进

初始语义抽取版本，后续需补充 db_tenant_code 与 app_tenant_code 的映射与转换规则。

相关页面：[[cust_company_info]] [[cust_role_info]]