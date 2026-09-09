---
type: concept
title: companyType
page_key: companyType
belong: concepts
domain: 门户侧边栏查询
status: published
aliases:
  - companyTypeCode
  - custType
  - 企业类型
  - 企业角色
oid: 1

sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: CustCompanyTypeEnum.dictKey / PlatformProductCustRoleDO.companyTypeCode / TenantProductMenuDO.companyType
adjudication: synonym
also_confused_with:
  - authRoleCode
scope:
  databases: [lowcode_pplatform]
---

companyType 是企业角色编码，在侧边栏查询菜单时作为输入参数，需要转换为授权角色 code（见 [[authRoleCode]]）才能查询权限菜单。该概念统一了企业角色在不同表（platform_product_cust_role、tenant_product_menu）和枚举（CustCompanyTypeEnum）中的字段对应关系。

## 需求背景

侧边栏企业角色下拉固定返回八个枚举值（[[queryCompanyType-固定企业角色集]]），其 key 即 companyType。在菜单查询链路 [[queryMenu-产品+企业角色菜单]] 中，companyType 被用于获取授权角色 code，因此必须明确其业务含义，避免与权限系统的 authRoleCode 混淆。

## 版本演进

当前 companyType 与固定枚举强绑定，若后续角色改为数据库配置，需要调整该概念映射和转换逻辑。