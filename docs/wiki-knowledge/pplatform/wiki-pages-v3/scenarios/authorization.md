---
type: scenario
title: 授权协议
page_key: authorization
domain: 授权协议与电子授权
status: draft
aliases: [授权书, 电子授权]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:授权协议与电子授权"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [authorization_agreement]
field_targets:
  - authorization_agreement.authed_status
  - authorization_agreement.creation_type
---

# 授权协议

问「已认证授权书 / 管理员变更产生的授权书」时进入本场景。

**主档** [[authorization_agreement]]：企业×产品授权确认书。`cust_name` / `company_type` 是写入时拷贝，不当 JOIN 键。  
**从属** [[argeement_migratory_record]]：协议迁移拉取记录（表名拼写以库为准）。

```ground:scenario
scenario: authorization
hubs:
- table: authorization_agreement
  role: master
  grain: 一企×一产品×一次授权书
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_id
  - cust_manager_id
  - platform_product_code
  - authed_status
  - creation_type
  - company_type
- table: argeement_migratory_record
  role: migrate
  grain: 一条协议拉取
  window:
  - id
  - enable
  - create_time
  - update_time
  - cust_id
  - platform_product_code
  - status
  - agreement_type
  - sign_mode
  - is_new
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
lifecycle: []
```
