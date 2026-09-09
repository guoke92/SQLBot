---
type: caliber
title: queryTenant-平台产品租户全集
page_key: queryTenant-平台产品租户全集
belong: calibers
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

该口径描述查询侧边栏租户列表时，当入参 productCode 为 ACCOUNT_PRODUCT 固定常量时的数据范围。系统返回 tenant_setting_config.activeList() 的全部生效租户，并将 dbTenantCode 映射为 tenantNo，name 映射为 tenantName。该分支覆盖平台产品场景，通常表示“全部租户”下拉选项。相关规则见 [[queryTenant_平台产品分流]]。

## 需求背景

侧边栏租户下拉需要根据当前选择的产品展示不同租户。平台产品 ACCOUNT_PRODUCT 代表全局账户产品，此时应展示所有生效租户，便于用户跨租户操作。

## 版本演进

初始版本，未对租户数量或分页进行限制，后续可能引入大数据量优化。

```ground:caliber
name: queryTenant-平台产品租户全集
predicate: queryProductReq.productCode = 'ACCOUNT_PRODUCT'
scope: 返回 tenant_setting_config.activeList() 的所有生效租户，转换为 tenantNo=dbTenantCode、tenantName=name
evidence: code_path:FbpSideBarQueryProcessor.queryTenant
```