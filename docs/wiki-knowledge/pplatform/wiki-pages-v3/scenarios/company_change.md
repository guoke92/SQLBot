---
type: scenario
title: 企业变更
page_key: company_change
domain: 企业变更与运营变更
status: draft
aliases: [企业信息变更]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:企业变更与运营变更", "db:db-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_change_record]
field_targets: [cust_change_record.status, cust_company_info.cust_status]
---

# 企业变更

问「变更中企业 / 变更审核中 / 自行变更单」时进入本场景。

**主档** [[cust_change_record]]：一笔企业信息变更单。  
**配置** [[cust_change_cfg]]：按认证方式、端类型、是否总公司匹配可变更项。  
**共享** [[cust_company_info]]：企业 `cust_status='CHANGE'` 表示变更中；`check_status` 是准入审核，不要和变更单 `status` 当成同一列。

运营人员变更流水 `cust_oper_change_record` 不是本场景主档。

```ground:scenario
scenario: company_change
hubs:
- table: cust_change_record
  role: master
  grain: 一次变更申请
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_id
  - alter_mode
  - status
  - need_cust_confirm
  - alter_type_id
  - cust_company_type
- table: cust_change_cfg
  role: config
  grain: 一条变更项配置
  window:
  - id
  - enable
  - create_time
  - update_time
  - item_code
  - plat_item
  - identify_style
  - client_type
  - head_company
  - open_process
shared:
- table: cust_company_info
  role: subject
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - cust_status
  - check_status
  - identify_style
  - head_company
  - data_type
lifecycle:
- enum: check_status
  process: cust_change_record_status
  field: cust_change_record.status
- enum: cust_status
  process: cust_status_flow
```
