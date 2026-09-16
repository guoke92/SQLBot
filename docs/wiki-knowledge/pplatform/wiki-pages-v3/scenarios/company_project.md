---
type: scenario
title: 企业项目绑定
page_key: company_project
domain: 项目报表/统计/上报
status: draft
aliases: [项目关联, 项目码]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:项目报表/统计/上报"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_project_rel]
field_targets:
  - cust_project_rel.project_id
  - cust_project_rel.company_type
---

# 企业项目绑定

问「某企业进了哪些项目 / 项目下供应商」时进入本场景。主档 [[cust_project_rel]]：企业×项目绑定，运营联系人、置顶、收费用企业角色都在这行。

[[cust_project_code_record]] 是企业录入项目码的对错记录。`project_id` 存的是 [[tenant_project]].id 的字符串形式。

```ground:scenario
scenario: company_project
hubs:
- table: cust_project_rel
  role: master
  grain: 一企×一项目
  window:
  - id
  - enable
  - create_time
  - update_time
  - project_id
  - product_id
  - channel_code
  - company_type
  - show_flag
  - top_flag
- table: cust_project_code_record
  role: code_audit
  grain: 一次项目码录入
  window:
  - id
  - enable
  - create_time
  - update_time
  - company_id
  - channel_code
  - status
  - type
shared:
- table: tenant_project
  role: project
  window:
  - id
  - enable
  - create_time
  - update_time
  - channel_code
  - platform_product_code
  - project_status
- table: cust_company_info
  role: company
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - name
lifecycle: []
```
