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
title: CA 预检（pre4Step）
page_key: CA-预检-pre4Step
domain: CA认证与服务费
aliases: []
---
# CA 预检（pre4Step）

登录/进入认证页时预检：调 cbsQueryCertInfo 查证书状态 + 证书登记企业名与 DB 企业名比对；证书失效或名称不匹配 → ca_register_status 重置 N（按主键 update）；企业处于变更流程（custStatus=CHANGE 或 custBuildStatus=CUST_CHANGE）直接阻断 CA 开通。certStatus=APPLYING 时 canProceed=false。

```ground:process
process: CA 预检（pre4Step）
stages:
- stage: CA 预检（pre4Step）
  trigger: 门户登录 / 一证四步入口
  effects:
  - op: update
    table: cust_company_info
    fields:
    - ca_register_status
  transitions: []
```

## 关联
- [[cust_company_info]]
