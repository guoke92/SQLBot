---
type: caliber
title: queryTenant-指定产品租户集
page_key: queryTenant-指定产品租户集
domain: 门户侧边栏查询
status: published
aliases: []
oid: 1

sources:
  - code_path:FbpSideBarQueryProcessor.queryTenant
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

该口径描述当入参 productCode 不是 ACCOUNT_PRODUCT 时，侧边栏租户列表的查询逻辑。系统首先按 tenant_product.platform_product_code 过滤得到租户编码集合，再通过 listByDbcodes 批量查询 tenant_setting_config 获取租户信息。若 tenant_product 无匹配或租户信息缺失，则返回 null。相关规则 [[queryTenant_平台产品分流]] 覆盖此分支。

## 需求背景

指定产品场景下，租户下拉选项应只包含已开通该产品的租户，用于缩小选择范围。该口径依赖 tenant_product 与 tenant_setting_config 的关联查询。

## 版本演进

当前返回 null 的行为可能是接口约定，若上游未处理 null 可能导致异常，后续应明确返回空列表还是 null，并统一错误语义。

```ground:caliber
name: queryTenant-指定产品租户集
predicate: queryProductReq.productCode != 'ACCOUNT_PRODUCT'
scope: 按 tenant_product.platform_product_code = 入参 productCode 查询，取 db_tenant_code 集合，再通过 listByDbcodes 查租户；若 tenant_product 无匹配或租户信息缺失返回 null
evidence: code_path:FbpSideBarQueryProcessor.queryTenant
```