---
type: scenario
title: 互通产品
page_key: interworking_product
domain: 租户产品/互通产品/租户项目
status: draft
aliases: [INTERWORKING]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:租户产品/互通产品/租户项目"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [tenant_interworking_product]
field_targets:
  - tenant_interworking_product.open_status
  - cust_interworking_product.open_status
---

# 互通产品

问「租户互通产品 / 企业开通的互通产品」时进入本场景，不要用 [[tenant_product]]。

租户层 `open_status` 仍是 Y/P/N；企业层 [[cust_interworking_product]] 用 [[cust_product_active]]。

```ground:scenario
scenario: interworking_product
hubs:
- table: tenant_interworking_product
  role: master
  grain: 一租户×一互通产品
  window:
  - id
  - enable
  - create_time
  - update_time
  - platform_product_code
  - open_status
  - target_sys_channel
  - scope
- table: tenant_interworking_project
  role: project_bind
  grain: 互通产品×项目
  window:
  - id
  - enable
  - create_time
  - update_time
  - product_id
  - project_id
  - platform_product_code
- table: cust_interworking_product
  role: cust_open
  grain: 一企×一互通产品
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_id
  - platform_product_code
  - open_status
  - product_id
lifecycle:
- enum: open_status
  process: interworking_open_flow
  field: tenant_interworking_product.open_status
- enum: cust_product_active
  process: cust_interworking_active_flow
  field: cust_interworking_product.open_status
shared: []
```
