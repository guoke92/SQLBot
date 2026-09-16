---
type: scenario
title: CA 证书认证
page_key: ca_cert
domain: CA证书认证
status: draft
aliases: [一证四步, CFCA, 开通电子签章]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:CA证书认证", "db:db-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [ca_certification_info]
field_targets: [ca_certification_info.submit_status, cust_company_info.ca_register_status]
---

# CA 证书认证

问「CA 已开通 / 上送失败 / 需要开通电子签章」时进入本场景，不要和收费台账 [[ca_fee]] 混用。收费看的是 `ca_fee_company.ca_status`（中台快照）与缴费状态；本场景看的是上送行与企业 `ca_register_status`。

**主档** [[ca_certification_info]]：一笔上送签章中台的认证行。  
**共享**：[[cust_company_info]] 提供企业身份与开通结论（`ca_register_status` / `need_register_ca`），不在本窗展开建档或缴费状态机。  
`ca_cfca_upgrade_report` 在计划里标记休眠，本窗不展开。

```ground:scenario
scenario: ca_cert
hubs:
- table: ca_certification_info
  role: master
  grain: 一次上送（cust_id + 来源批次）
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_id
  - cust_type
  - data_source
  - op_type
  - submit_status
  - head_company_data
shared:
- table: cust_company_info
  role: identity_and_open_status
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - certification_no
  - name
  - need_register_ca
  - ca_register_status
lifecycle:
- enum: ca_submit_status
  process: ca_submit_status_flow
- enum: open_status
  process: ca_register_status_flow
```
