---
type: enum
title: receive_payment_type
page_key: receive_payment_type
domain: 基线
status: draft
aliases: []
oid: 1
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# receive_payment_type

（权威枚举页：2 值，绑定方式 exact-name，主承载 cust_account_info.receive_payment_type；db 实测分布。）

```ground:enum
enum: receive_payment_type
fields: [cust_account_info.receive_payment_type]
values:
  1:
    label: 收款
  2:
    label: 付款
```
