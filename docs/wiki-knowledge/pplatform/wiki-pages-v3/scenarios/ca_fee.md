---
type: scenario
title: CA 证书收费
page_key: ca_fee
domain: CA证书收费
status: draft
aliases: [CA服务费, 企业缴费, 收费台账]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:CA证书收费", "db:db-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [ca_fee_company]
field_targets: [ca_fee_company.pay_status, ca_fee_order.order_status]
---

# CA 证书收费

问「已缴费企业 / 待缴订单 / 即将到期」时进入本场景，而不是从全库表目录起步。

**主档** [[tables/ca_fee_company]]：一企一行，企业级缴费快照与服务期。  
**从属**：订单流水 [[tables/ca_fee_order]]、项目开关 [[tables/ca_fee_project_config]]。  
**共享（非本场景主档）**：[[tables/cust_company_info]] 只提供企业身份（`code` / 信用代码），不在本窗展开建档流转。

企业级 `pay_status` 与订单级 `order_status` 不是同一列，见 [[concepts/paid]]。

```ground:scenario
scenario: ca_fee
hubs:
- table: ca_fee_company
  role: master
  grain: 一企一行（certification_no）
  window:
  - id
  - enable
  - create_time
  - update_time
  - certification_no
  - company_name
  - pay_status
  - ca_status
  - service_start
  - service_end
  - renew_remind_sent
  - special_config_flag
  - special_annual_fee
  - fee_locked
  - locked_annual_fee
  - source_project_id
  - source_company_type
- table: ca_fee_order
  role: ledger
  grain: 一次缴费/续费/补录
  window:
  - id
  - enable
  - create_time
  - update_time
  - order_no
  - certification_no
  - project_id
  - company_type
  - order_status
  - order_type
  - agreement_signed
  - annual_fee
  - pay_amount
  - pay_time
  - service_start
  - service_end
  - invoice_status
  - bocom_txn_sts
- table: ca_fee_project_config
  role: config
  grain: 一项目一行
  window:
  - id
  - enable
  - create_time
  - update_time
  - project_id
  - charge_enabled
  - core_annual_fee
  - supplier_annual_fee
  - special_company_list
shared:
- table: cust_company_info
  role: identity
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - certification_no
  - name
lifecycle:
- enum: pay_status
  process: ca_fee_company_pay_status
- enum: order_status
  process: ca_fee_order_status
- field: ca_fee_company.renew_remind_sent
  process: ca_fee_renew_remind
```
