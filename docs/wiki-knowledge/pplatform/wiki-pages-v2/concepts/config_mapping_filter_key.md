---
type: concept
title: 配置映射过滤键
page_key: config_mapping_filter_key
domain: 平台产品配置
status: draft
aliases: [outerChannel, productCode, platformProductCode]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustProductDomainService.java#getProductCompanyTypeConfig
contract_version: "0.1"
maps_to: cust_config_mapping.outer_channel
also_confused_with:
  - cust_config_mapping.inner_code
adjudication: boundary
boundary: "getProductCompanyTypeConfig 实际传参为 (type='COMPANY_TYPE_MAPPING', innerCode=companyType, outerChannel=platformProductCode)，outer_channel 存的是平台产品编码而非渠道。"
belong: concepts
field_targets: [cust_config_mapping.outer_channel]
---

「配置映射过滤键」澄清 [[cust_config_mapping]] 三个键位的实际语义：`outer_channel` 在平台产品域被当作平台产品编码使用，`inner_code` 存企业角色码，`type` 为映射类型（如 COMPANY_TYPE_MAPPING）。字段名与内容不一致，阅读需求文档时须按内容而非名称理解。

## 需求背景

企业角色到平台产品编码的映射查询依赖该三元组，配合 [[config_mapping_enabled]] 过滤；角色语义见 [[company_type]]，产品编码语义见 [[platform_product_code]]。

## 版本演进

- 字段名沿用渠道语义，实现在产品域复用后语义漂移，暂不改名，仅以本页裁定。

关联：[[cust_config_mapping]]、[[platform_product_code]]、[[company_type]]、[[config_mapping_enabled]]