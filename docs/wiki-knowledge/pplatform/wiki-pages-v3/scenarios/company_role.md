---
type: scenario
title: 企业角色与端口
page_key: company_role
domain: 客户角色与端口
status: draft
aliases: [企业角色, 产品端口]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:客户角色与端口"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_role_info]
field_targets:
  - cust_role_info.role_type
  - cust_role_info.status
---

# 企业角色与端口

问「企业有哪些角色 / 某产品支持哪些企业角色」时进入本场景。

**主档** [[cust_role_info]]：一企×一角色类型一行，看角色是否激活。  
**配置** [[platform_product_cust_role]]：平台产品允许的企业角色矩阵，不是客户状态。

`role_type` 与联系人 `company_type` 共用 [[company_type]] 字典，粒度不同：角色是企业切片，联系人是人绑在该切片上。

```ground:scenario
scenario: company_role
hubs:
- table: cust_role_info
  role: master
  grain: 一企×一角色类型
  window:
  - id
  - enable
  - create_time
  - update_time
  - ref_cust_company_info
  - role_type
  - status
  - platform_cust_id
  - ref_cust_auth_application
- table: platform_product_cust_role
  role: config
  grain: 一产品×一企业角色
  window:
  - id
  - enable
  - create_time
  - update_time
  - product_code
  - company_type_code
  - company_type_name
shared:
- table: cust_company_info
  role: identity
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - cust_company_type
lifecycle:
- enum: activate_status
  process: role_status_flow
  field: cust_role_info.status
```
