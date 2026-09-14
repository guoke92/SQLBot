---
type: enum
title: account_type
page_key: account_type
domain: 企业银行账户
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---









# 账户类型 account_type

`cust_account_info.account_type` 对应 `AccountTypeEnum`。访问器不要写反：

- `getDictKey()` = `"1"` / `"2"` / `"3"` / `"received"` / `"payment"`
- `getDictParam()` 与 `.name()` = `BANK` / `THIRD_PARTY_PAYMENT_AGENCY` / …

DB 主路径是 `.name()`：`BANK` 48428 条；dictKey `"1"` 仅 5 条遗留。另有代码未声明的 `OPERATION_FEE_ACCOUNT` 30 条。

## 需求背景

账户类型是账户统计的主口径之一。只按 `BANK` 过滤会漏掉运营费账户。

## 版本演进

- `BANK` 为绝对主值，与 `.name()` / `getDictParam()` 落库一致。
- `'1'` 仅 5 条，是 `getDictKey()` 遗留，不要当成当前写值点。
- `received` 仅 1 条，走 `getDictKey()`。
- `OPERATION_FEE_ACCOUNT` 30 条，枚举类未声明。

```ground:enum
enum: account_type
fields: [cust_account_info.account_type]
values:
  "SELF":
    label: "企业自身"
  "THIRD":
    label: "三方"
  "1":
    label: "银行"
    java_name: "BANK"
  "BANK":
    label: "银行"
    stored_as: name
    note: "与 dictKey 1 同常量；.name()/getDictParam 落库"
  "2":
    label: "第三方支付机构"
    java_name: "THIRD_PARTY_PAYMENT_AGENCY"
  "3":
    label: "开票"
    java_name: "INVOICING"
  "received":
    label: "收款"
    java_name: "RECEIVED"
    note: "DB 1 条，低频 getDictKey()"
  "payment":
    label: "付款"
    java_name: "PAYMENT"
  "OPERATION_FEE_ACCOUNT":
    label: "运营费账户"
    note: "db 分布存在但代码枚举未声明（REVIEW）"
```
