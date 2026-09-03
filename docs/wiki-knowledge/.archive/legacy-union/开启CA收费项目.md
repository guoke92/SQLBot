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
type: caliber
title: 开启CA收费项目
page_key: 开启CA收费项目
domain: ca_fee
field_targets:
- ca_fee_project_config.charge_enabled
- ca_fee_project_config.enable
---
# 开启CA收费项目

项目配置charge_enabled=Y且启用。

```ground:caliber
caliber: 开启CA收费项目
field_targets:
- ca_fee_project_config.charge_enabled
- ca_fee_project_config.enable
filters:
- .ca_fee_project_config.charge_enabled = 'Y'
- .ca_fee_project_config.enable = 'Y'
```

## 关联
- [[ca_fee_project_config]]
