---
type: concept
title: 平台产品编码
page_key: platform_product_code
domain: 平台产品配置
status: draft
aliases: [productCode, platformProductCode, product_code, platform_product_code]
oid: 1
scope:
  databases: [platform]
sources:
  - db:platform_product.product_code
  - code:PlatformProductApplication.java
contract_version: "0.1"
maps_to: platform_product.product_code
also_confused_with:
  - platform_product.platform_code
adjudication: boundary
boundary: "product_code 为产品级编码(ACFLOW/AMS/DRAFT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER)；platform_code 为平台级编码(AMS/DRAFT/HTCP*/PPLATFORM/XYC)，两者不可互换。"
belong: concepts
field_targets: [platform_product.product_code]
---

「平台产品编码」指产品级唯一键 `platform_product.product_code`，是跨表引用、事件路由与列表白名单过滤的统一键值。与「平台编码」`platform_code` 形近义异，不可互换。

## 需求背景

向下游传递时以 `platformProductCode` 出现，例如 [[tenant_product]] 的 `platform_product_code` 与 [[cust_config_mapping]] 的 `outer_channel`；白名单过滤见 [[list_whitelist_filter]]。

## 版本演进

- 产品级编码与平台级编码自始分列，未发生合并或改名。

关联：[[platform_product]]、[[tenant_product]]、[[cust_config_mapping]]、[[list_whitelist_filter]]、[[config_mapping_filter_key]]