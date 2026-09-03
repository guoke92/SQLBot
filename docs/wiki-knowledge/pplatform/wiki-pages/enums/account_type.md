---
type: enum
title: account_type
page_key: account_type
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

# account_type

（权威枚举页：7 值，绑定方式 setter-evidence，主承载 cust_account_info.account_type；db 实测分布，基线外 2 值。）

```ground:enum
enum: account_type
fields: [cust_account_info.account_type]
values:
  SELF:
    label: 企业自身
  THIRD:
    label: 三方
  1:
    label: 银行
  2:
    label: 第三方支付机构
  3:
    label: 开票
  received:
    label: 收款
  payment:
    label: 付款
  BANK:
    label: "BANK"
    note: db 分布存在但代码枚举未声明（REVIEW）
  OPERATION_FEE_ACCOUNT:
    label: "OPERATION_FEE_ACCOUNT"
    note: db 分布存在但代码枚举未声明（REVIEW）
```
