---
type: scenario
title: 企业建档
page_key: company_build
domain: 企业建档与认证状态机
status: draft
aliases: [企业认证, 客户建档]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:企业建档与认证状态机", "db:db-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_company_info]
field_targets: [cust_company_info.cust_build_status, cust_company_info.cust_status, cust_company_info.data_type]
---

# 企业建档

问「建档成功企业 / 待客户认证 / 生效客户」时进入本场景。

**主档** [[tables/cust_company_info]]：平台企业主数据，一行一个企业。  
`cust_build_status` 是认证过程，`cust_status` 是企业本身状态。`data_type` 区分主数据行和流程行，见 [[data_type]]。

认证开关（打款次数、人脸、是否审核）在共享配置 [[cust_setting_config]]，不是主档状态机。本表同时被 [[ca_fee]] 等场景引用为身份源——那些窗口不把建档流转当缴费或开通状态用。

```ground:scenario
scenario: company_build
hubs:
- table: cust_company_info
  role: master
  grain: 一企一行（code）
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - certification_no
  - name
  - cust_build_status
  - cust_status
  - cust_company_type
  - identify_style
  - data_type
shared:
- table: cust_setting_config
  role: auth_config
  window:
  - id
  - enable
  - create_time
  - update_time
  - need_auth_verify
  - face_recognition
  - payment_verification
  - payment_maximum_number
lifecycle:
- enum: cust_build_status
  process: cust_build_status_flow
- enum: cust_status
  process: cust_status_flow
```
