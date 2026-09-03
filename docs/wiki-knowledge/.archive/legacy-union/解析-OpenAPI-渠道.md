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
title: 解析 OpenAPI 渠道
page_key: 解析-OpenAPI-渠道
domain: openapi
aliases: []
---
# 解析 OpenAPI 渠道



```ground:process
process: 解析 OpenAPI 渠道
stages:
- stage: 解析 OpenAPI 渠道
  trigger: OpenAPI 请求携带 channel
  effects:
  - op: read
    table: cust_access_secret
    fields:
    - channel
    - enable
    - db_tenant_code
  transitions: []
```

## 关联
- [[cust_access_secret]]
