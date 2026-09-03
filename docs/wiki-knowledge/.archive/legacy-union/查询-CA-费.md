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
title: 查询 CA 费
page_key: 查询-CA-费
domain: ca_fee
aliases: []
---
# 查询 CA 费



```ground:process
process: 查询 CA 费
stages:
- stage: 查询 CA 费
  trigger: /cust-web/caFee
  effects:
  - op: read
    table: ca_fee_company
    fields:
    - pay_status
    - ca_status
    - enable
  transitions: []
```

## 关联
- [[ca_fee_company]]
