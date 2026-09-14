---
type: enum
title: auth_state
page_key: auth_state
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





# 打款认证状态 auth_state

`cust_account_info.auth_state` 的枚举为 `AccountAuthState`，取值形如 `APPLY_00`~`APPLY_40`，状态迁移见 [[bank_account_auth_state]]。审计发现同一枚举“写值用 `getDictParam()`、查询用 `getDictKey()`”，存在键形态混用风险，需确认存储形态。

## 需求背景

该字段是[[payment_auth]]流程的阶段标记，决定账户能否继续发起打款、能否进入金额验证，也是[[not_applied_payment_auth]]与“已完成验证”口径的依据。

## 版本演进

- `APPLY_00` 为 DB 列默认值，占 49144 条，是存量主状态。
- `APPLY_20`、`APPLY_40` 已在生产数据出现；`APPLY_10`、`APPLY_30` 仅在代码常量中出现。
- `APPLY_10` 的审计结论为 reject：写值点用 `getDictParam()`、查询点用 `getDictKey()`，键形态不一致，审计备注在给定材料中被截断。

```ground:enum
enum: auth_state
fields: [cust_account_info.auth_state]
values:
  "APPLY_00":
    label: "APPLY_00"
  "APPLY_20":
    label: "APPLY_20"
  "APPLY_40":
    label: "APPLY_40"
  "APPLY_10":
    label: "打款申请已提交"
    java_name: "AccountAuthState.APPLY_10"
    stored_as: 写值用 getDictParam()、查询用 getDictKey()
    note: "同一枚举写值与查询使用了不同的键取法，存在键形态混用风险；审计备注在语义分析中被截断，需回源码确认落库形态"
```