---
type: concept
title: productCode
page_key: productCode
domain: 门户侧边栏查询
status: published
aliases:
  - platformProductCode
  - PLATFORM_PRODUCT_CODE
oid: 1

sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: QueryProductReq.productCode / TenantProductDO.platformProductCode / PlatformProductCustRoleDO.productCode / TenantProductMenuDO.productCode
adjudication: synonym
also_confused_with:
  - systemCode
  - ACCOUNT_PRODUCT
scope:
  databases: [lowcode_pplatform]
---

productCode 是产品编码，在侧边栏查询中扮演关键角色：请求入参、租户产品关联、角色关联、菜单配置等均使用该字段。侧边栏固定使用常量 ACCOUNT_PRODUCT 作为平台产品 code，其他产品 code 由请求传入。该概念衔接多个表字段和请求对象。

## 需求背景

productCode 的分支判断决定了租户查询口径（[[queryTenant-平台产品租户全集]] 与 [[queryTenant-指定产品租户集]]）。同时，查询菜单时 productCode 必须等于 ACCOUNT_PRODUCT（[[queryMenu-产品+企业角色菜单]]）。明确该术语有助于理解产品的边界。

## 版本演进

当前 ACCOUNT_PRODUCT 是硬编码常量，若未来支持多平台产品，需要将常量改为配置或参数化。