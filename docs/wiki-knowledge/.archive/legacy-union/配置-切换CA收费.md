---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: process
title: 配置/切换CA收费
page_key: 配置-切换CA收费
domain: cafee
aliases: []
---
# 配置/切换CA收费



```ground:process
process: 配置/切换CA收费
stages:
- stage: 配置/切换CA收费
  trigger: 运营后台保存项目配置或切换收费开关
  effects:
  - op: upsert
    table: ca_fee_project_config
    fields:
    - project_id
    - tenant_id
    - charge_enabled
    - supplier_annual_fee
    - core_annual_fee
    - pay_channel
    - special_company_list
    - agreement_version
    - last_toggle_time
  transitions: []
```

## 关联
- [[ca_fee_project_config]]
