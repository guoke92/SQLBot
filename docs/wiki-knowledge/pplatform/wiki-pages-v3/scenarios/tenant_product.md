---
type: scenario
title: 租户通用产品
page_key: tenant_product
domain: 租户产品/互通产品/租户项目
status: draft
aliases: [租户产品开通]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:租户产品/互通产品/租户项目"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [tenant_product]
field_targets:
  - tenant_product.open_status
---

# 租户通用产品

问「租户开通了哪些通用产品」时进入本场景。只覆盖 `product_type=GENERAL` 落到 [[tenant_product]] 的那条线；互通产品见 [[interworking_product]]，可运行实例见 [[tenant_project]]。

租户开通列是 Y/P/N 的 [[open_status]]，和企业开通 [[cust_product_active]]（NOT_OPENED/OPENING/OPENED）不是同一字典。

```ground:scenario
scenario: tenant_product
hubs:
- table: tenant_product
  role: master
  grain: 一租户×一平台产品
  window:
  - id
  - enable
  - create_time
  - update_time
  - platform_product_id
  - platform_product_code
  - open_status
  - ref_tenant_product_tenant_setting_config
- table: tenant_product_menu
  role: menu
  grain: 产品×企业角色×菜单
  window:
  - id
  - enable
  - create_time
  - update_time
  - product_code
  - company_type
  - menu_id
- table: tenant_product_menu_res
  role: menu_res
  grain: 菜单资源
  window:
  - id
  - enable
  - create_time
  - update_time
  - product_code
  - company_type
  - menu_id
shared:
- table: platform_product
  role: catalog
  window:
  - id
  - enable
  - create_time
  - update_time
  - product_code
  - product_type
  - product_status
lifecycle:
- enum: open_status
  process: tenant_product_open_flow
  field: tenant_product.open_status
```
