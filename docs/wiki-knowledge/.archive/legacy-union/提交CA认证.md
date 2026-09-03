---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: process
title: 提交CA认证
page_key: 提交CA认证
domain: certification
aliases: []
---
# 提交CA认证



```ground:process
process: 提交CA认证
stages:
- stage: 提交CA认证
  trigger: 企业/个人发起 CA 认证
  effects:
  - op: insert
    table: ca_certification_info
    fields:
    - cust_id
    - cust_type
    - submit_status
    - submit_time
    - op_type
    - batch_no
  transitions: []
```

## 关联
- [[ca_certification_info]]
