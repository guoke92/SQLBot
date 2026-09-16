---
type: scenario
title: 平台产品配置
page_key: platform_product
domain: 平台产品配置
status: draft
aliases: [产品目录, 通用产品, 互通产品]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:平台产品配置"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [platform_product]
field_targets:
  - platform_product.product_code
  - platform_product.product_status
---

# 平台产品配置

问「平台有哪些已生效产品 / 通用还是互通」时进入本场景。这是全局产品模板，不是租户开通、也不是企业开通。

**主档** [[platform_product]]。从属：客户端 [[platform_product_client]]、企业定制入口 [[cust_customized_product]]、内外码映射 [[cust_config_mapping]]。产品允许的企业角色在 [[company_role]] 的配置表。  
`cust_app_channel_config` 无 Java DO，本窗不展开。

```ground:scenario
scenario: platform_product
hubs:
- table: platform_product
  role: master
  grain: 一个平台产品
  window:
  - id
  - enable
  - create_time
  - update_time
  - product_code
  - product_type
  - product_status
  - multiple_project_flag
  - wkfl_flag
  - basic_product
- table: platform_product_client
  role: client
  grain: 产品×客户端
  window:
  - id
  - enable
  - create_time
  - update_time
  - platform_product_id
  - client_type
  - status
  - link_type
- table: cust_customized_product
  role: customized
  grain: 企业定制入口
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_id
  - url
- table: cust_config_mapping
  role: mapping
  grain: 一条内外码
  window:
  - id
  - enable
  - create_time
  - update_time
  - type
  - outer_channel
  - inner_code
  - outer_code
  - groups
lifecycle:
- enum: product_status
  process: product_status_flow
shared: []
```
