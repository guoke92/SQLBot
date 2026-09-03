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
type: enum
title: 项目CA收费
page_key: project_id
domain: ca_fee
aliases:
- CA收费开关
- 项目收费配置
anchors:
- project_id
---
# 项目CA收费

项目是否开启CA收费及不同企业角色的年费配置。

```ground:enum
enum: project_id
fields:
- ca_fee_project_config.project_id
- ca_fee_project_config.charge_enabled
values:
  Y:
    label: 收费
  N:
    label: 不收费
```

## 关联
- [[ca_fee_project_config|ca_fee_project_config]]
