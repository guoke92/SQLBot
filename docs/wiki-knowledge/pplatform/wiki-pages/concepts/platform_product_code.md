---
type: concept
title: 平台产品编码
page_key: concept/platform_product_code
domain: 支付宝蚂蚁档案与清算
status: published
aliases: ["productCode", "platformProductCode", "routeProductCode", "productAppId"]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: platform_product_code
field_targets: []
adjudication: synonym
also_confused_with: ["appId", "productCodeEnum"]
scope:
  databases: [lowcode_pplatform]
---

平台产品编码用于标识支付宝清分场景中的产品。该术语存在多个别名，其中 productCode 是业务产品编码，productAppId 是同步调用中的产品应用标识，二者在支付宝清分配置场景中可互相替代。需要与 appId 和 productCodeEnum 区分。

## 需求背景

支付宝清分查询与同步调用中需要路由到具体产品，平台产品编码是核心路由参数。默认值为 ACFLOW 时确保无编码也能执行查询。

## 版本演进

初始定义，暂无变更。边界说明来自语义分析 term_bridges。

[[tables/ProjectAlipayClearingConfigQryDTO]] [[rules/客户端查询平台产品编码必填]] [[rules/同步调用点 productAppId 构建]]