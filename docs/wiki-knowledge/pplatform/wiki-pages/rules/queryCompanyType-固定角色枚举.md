---
type: rule
title: queryCompanyType 固定角色枚举
page_key: queryCompanyType-固定角色枚举
belong: rules
domain: 门户侧边栏查询
status: published
aliases: []
oid: 1

sources:
  - code_path:FbpSideBarQueryProcessor.queryCompanyType
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该规则规定侧边栏企业角色下拉固定返回八个 CustCompanyTypeEnum 枚举值，不读取数据库配置，顺序为 FINANCE、SUPPLIER、CORE、CORE_MANAGER、PROJECT_COMPANY、DEALER、PLATFORM_OPERATOR_COMPANY、CORPORATION_COMPANY。该规则使角色过滤选项不受 platform_product_cust_role 表配置影响，相关口径 [[queryCompanyType-固定企业角色集]]。

## 需求背景

当前产品需要统一的企业角色选项，避免因数据库配置差异导致不同环境角色不一致。该规则通过硬编码枚举实现全局一致。

## 版本演进

若后续角色需要产品级动态配置，需移除硬编码并改为读取 platform_product_cust_role 表，同时处理迁移兼容。

```ground:rule
name: queryCompanyType 固定角色枚举
content: 侧边栏企业角色下拉固定返回八个 CustCompanyTypeEnum，不读取数据库配置，顺序为 FINANCE、SUPPLIER、CORE、CORE_MANAGER、PROJECT_COMPANY、DEALER、PLATFORM_OPERATOR_COMPANY、CORPORATION_COMPANY
impact: 角色过滤选项不受 platform_product_cust_role 表配置影响
field_targets:
  - queryCompanyType
evidence: code_path:FbpSideBarQueryProcessor.queryCompanyType
```