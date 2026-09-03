---
type: rule
title: queryTenant 平台产品分流
page_key: queryTenant 平台产品分流
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

该规则描述了侧边栏租户查询时根据产品编码进行分支的逻辑：当入参 productCode 为 ACCOUNT_PRODUCT 时返回所有生效租户；否则按 tenant_product.platform_product_code 过滤租户。若未匹配到租户或租户信息缺失则返回 null。该规则直接影响租户下拉选项的数据来源，并关联口径 [[queryTenant-平台产品租户全集]] 与 [[queryTenant-指定产品租户集]]。

## 需求背景

侧边栏租户下拉需要区分平台产品与普通产品，以实现不同的数据范围策略。该规则确保了平台产品场景下的“全部租户”与普通产品场景下的“过滤租户”行为。

## 版本演进

当前普通产品分支返回 null 可能被调用方误判，后续建议统一返回空列表，或补充错误码约定。

```ground:rule
name: queryTenant 平台产品分流
content: 当入参 productCode 为 ACCOUNT_PRODUCT 时返回所有生效租户；否则按 tenant_product.platform_product_code 过滤租户，若未匹配到租户或租户信息缺失则返回 null（平台产品分支返回空列表）
impact: 影响侧边栏租户下拉选项的数据源
field_targets:
  - queryProductReq.productCode
  - tenant_product.platform_product_code
  - tenant_setting_config.db_tenant_code
evidence: code_path:FbpSideBarQueryProcessor.queryTenant
```