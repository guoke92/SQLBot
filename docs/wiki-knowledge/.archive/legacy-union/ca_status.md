---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: CA签章状态
page_key: ca_status
domain: CA认证与服务费
aliases:
- CA证书有效
- CA证书过期
- CA已注销
anchors:
- ca_status
---
# CA签章状态

ca_fee_company.ca_status 来自签章中台实时值。注意与服务费状态（pay_status）同名 不同义：ca_status 是证书有效性，pay_status 是缴费。

```ground:enum
enum: ca_status
fields:
- ca_fee_company.ca_status
values:
  NORMAL:
    label: 有效
  EXPIRED:
    label: 已过期
  CANCELLED:
    label: 已注销
  UNREGISTERED:
    label: 未注册
  UNKNOWN:
    label: 未注册（兜底）
```

## 关联
- [[ca_fee_company|ca_fee_company]]
