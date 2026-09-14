---
type: concept
title: productCode 平台产品编码
page_key: productCode
domain: 平台产品配置
status: draft
aliases: [productCode, platformProductCode, 平台产品编码]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:platform_product.product_code
  - code:tenant_product.platform_product_code
  - code:cust_auth_application.platform_product_code
maps_to: platform_product.product_code
adjudication: synonym
also_confused_with: [code]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
belong: concepts
field_targets: [platform_product.product_code]
---

productCode 与 platformProductCode 在代码中常混用，二者均指平台产品编码，映射到 [[tables/platform_product]] 的 `product_code`。

边界：`platform_product.code` 是内部编码，不对外使用，不要与 `product_code` 混为一谈。对外传递、白名单过滤（[[calibers/platform-product-whitelist]]）与租户/客户产品关联所使用的都是 `product_code`。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 表：[[tables/platform_product]]、[[tables/tenant_product]]、[[tables/cust_auth_application]]
- 规则：[[rules/platform-product-save-check]]、[[rules/platform-product-list-filter]]
- 口径：[[calibers/platform-product-whitelist]]

相关：[[platform_product]]
