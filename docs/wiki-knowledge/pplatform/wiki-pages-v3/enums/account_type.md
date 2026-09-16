---
type: enum
title: account_type
page_key: account_type
domain: 企业银行账户/集团/SFTP
status: draft
aliases: [银行账户]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# account_type

`AccountTypeEnum`：dictKey `'1'` 银行 / `'2'` 第三方支付机构 / `'3'` 开票 / `received` 收款 / `payment` 付款。联系人保存写入 `getDictParam()`=`BANK`。库以 `BANK` 为主，另有少量 `'1'` 与代码外 `OPERATION_FEE_ACCOUNT`。问银行账户过滤 `BANK`。

```ground:enum
enum: account_type
fields:
  - cust_account_info.account_type
values:
  "1":
    label: "银行"
  "2":
    label: "第三方支付机构"
  "3":
    label: "开票"
  "received":
    label: "收款"
  "payment":
    label: "付款"
  "BANK": {}
  "OPERATION_FEE_ACCOUNT": {}
```
