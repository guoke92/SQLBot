---
type: scenario
title: 租户项目
page_key: tenant_project
domain: 租户产品/互通产品/租户项目
status: draft
aliases: [项目实例]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:租户产品/互通产品/租户项目"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [tenant_project]
field_targets:
  - tenant_project.project_status
---

# 租户项目

问「已生效项目 / 待生效项目」时进入本场景。一行是租户下可运行的项目实例，`product_id` 指向 [[tenant_product]].id。

运营文件元数据 [[project_file_info]] 挂在本窗。企业绑项目见 [[company_project]]；上线审批见 [[project_online_approval]]；企微立项统计见 [[wechat_project_stats]]。

```ground:scenario
scenario: tenant_project
hubs:
- table: tenant_project
  role: master
  grain: 一个租户项目
  window:
  - id
  - enable
  - create_time
  - update_time
  - project_status
  - channel_code
  - platform_product_code
  - product_id
  - project_approval_id
  - wechat_audit_no
  - source
- table: project_file_info
  role: files
  grain: 项目下一份运营文件
  window:
  - id
  - enable
  - create_time
  - update_time
  - project_id
  - file_type
  - title
shared:
- table: tenant_product
  role: product
  window:
  - id
  - enable
  - create_time
  - update_time
  - platform_product_code
  - open_status
lifecycle:
- enum: project_status
  process: project_status_flow
```
