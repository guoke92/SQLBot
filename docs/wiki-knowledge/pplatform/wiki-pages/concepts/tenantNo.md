---
type: concept
title: tenantNo
page_key: tenantNo
domain: 门户侧边栏查询
status: published
aliases:
  - dbTenantCode
  - tenantCode
oid: 1

sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: TenantRes.tenantNo = TenantDTO.dbTenantCode
adjudication: synonym
also_confused_with:
  - appTenantCode
scope:
  databases: [lowcode_pplatform]
---

tenantNo 是侧边栏响应中承载数据租户标识的字段名，其取值为 tenant_setting_config.db_tenant_code。该概念用于明确前端字段与后端租户编码的映射关系，避免与逻辑租户 appTenantCode 混淆。

## 需求背景

在 [[queryTenant-平台产品租户全集]] 和 [[queryTenant-指定产品租户集]] 两个口径中，返回给前端的租户编码字段统一使用 tenantNo，而后端存储字段为 dbTenantCode。需要建立术语桥接，确保代码和文档一致。

## 版本演进

该映射在当前版本稳定，后续若引入租户别名或多租户模型，需重新评估映射边界。