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
type: enum
title: CA开通状态
page_key: ca_register_status
domain: CA认证与服务费
aliases:
- 已开通CA
- 未开通
- 开通中
- CA开通状态
- 证书状态
- CA已开通
- CA失效
anchors:
- ca_register_status
---
# CA开通状态

cust_company_info.ca_register_status：N→Y（openCa 成功）；Y→N（变更企业名/ 证书失效重置）。与 ca_certification_info.submit_status 不同维度—— ca_register_status 是企业维度开通标记，submit_status 是单次报数行状态。

```ground:enum
enum: ca_register_status
fields:
- cust_company_info.ca_register_status
values:
  Y:
    label: 已开通
  N:
    label: 未开通
  P:
    label: 开通中（过渡）
```

## 关联
- [[cust_company_info|cust_company_info]]
