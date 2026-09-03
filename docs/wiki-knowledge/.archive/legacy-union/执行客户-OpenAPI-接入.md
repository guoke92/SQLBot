---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:openapi-access@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: process
title: 执行客户 OpenAPI 接入
page_key: 执行客户-OpenAPI-接入
domain: openapi
aliases: []
---
# 执行客户 OpenAPI 接入



```ground:process
process: 执行客户 OpenAPI 接入
stages:
- stage: 执行客户 OpenAPI 接入
  trigger: 渠道与租户校验通过
  effects:
  - op: upsert
    table: client_api_sync_error
    fields:
    - service_class_name
    - param
    - create_time
    - enable
    - retry_num
  transitions: []
```

## 关联
- [[client_api_sync_error]]
