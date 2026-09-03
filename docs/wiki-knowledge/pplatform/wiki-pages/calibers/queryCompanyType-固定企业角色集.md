---
type: caliber
title: queryCompanyType-固定企业角色集
page_key: queryCompanyType-固定企业角色集
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

该口径描述侧边栏企业角色下拉的数据来源，固定返回八个 CustCompanyTypeEnum 枚举值，不读取数据库配置。返回结构为 key=dictKey、value=displayName。相关规则 [[queryCompanyType_固定角色枚举]] 详细说明。

## 需求背景

企业角色下拉用于过滤菜单或导航，当前产品要求固定角色集合，因此不依赖 platform_product_cust_role 表配置，保证所有环境一致。

## 版本演进

若未来角色需要产品级差异化，需迁移到读取 platform_product_cust_role 表，并处理固定枚举与配置角色的合并策略。

```ground:caliber
name: queryCompanyType-固定企业角色集
predicate: 无条件
scope: 返回硬编码的八个 CustCompanyTypeEnum：FINANCE、SUPPLIER、CORE、CORE_MANAGER、PROJECT_COMPANY、DEALER、PLATFORM_OPERATOR_COMPANY、CORPORATION_COMPANY，转换为 key=dictKey、value=displayName
evidence: code_path:FbpSideBarQueryProcessor.queryCompanyType
```