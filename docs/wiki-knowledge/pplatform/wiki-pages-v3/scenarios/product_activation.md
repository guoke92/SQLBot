---
type: scenario
title: 企业产品开通
page_key: product_activation
domain: 自动审核与工作流审核
status: draft
aliases: [产品开通, 开通应用]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:自动审核与工作流审核"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_auth_application]
field_targets:
  - cust_auth_application.open_status
---

# 企业产品开通

问「企业已开通哪些产品 / 开通中」时进入本场景。计划 topic 名叫自动审核，落库主档其实是企业×租户产品开通行 [[cust_auth_application]]。自动核验写在建档侧认证快照，不在本表。

`open_status` 取值 `NOT_OPENED` / `OPENING` / `OPENED`，不要和租户产品 [[open_status]]（Y/P/N）或企业 CA `ca_register_status` 混列。

`cust_auth_application_config` 无 Java DO、库空，本窗不展开。

```ground:scenario
scenario: product_activation
hubs:
- table: cust_auth_application
  role: master
  grain: 一企×一租户产品
  window:
  - id
  - enable
  - create_time
  - update_time
  - ref_cust_company_info
  - ref_cust_auth_application_tenant_product
  - platform_product_code
  - open_status
  - open_time
shared:
- table: cust_company_info
  role: identity
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - name
- table: tenant_product
  role: tenant_product
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - platform_product_code
  - open_status
lifecycle:
- enum: cust_product_active
  process: cust_product_active_flow
```
