---
type: rule
title: 验证失败不落库
page_key: verify_fail_not_persisted
domain: 企业银行账户
status: draft
aliases:
  - 打款验证失败状态未持久化
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 验证失败不落库

`result=1/2` 分支在 `setErrorTryCount`/`setErrorTryTime` 之后、`saveOrUpdate` 之前直接 `throw`，且方法无事务注解，错误次数与 `APPLY_40` 实际不会持久化，属实现与设计不一致。

## 需求背景

设计意图是记录失败次数与时间（`error_try_count`/`error_try_time`）以便风控与运营跟进，同时把状态推进到 `APPLY_40`；实现上失败分支提前抛出，导致状态机中两条指向 `APPLY_40` 的迁移（见 [[bank_account_auth_state]]）实际不成立，[[auth_state]] 的失败态观测缺失。

## 版本演进

- 该问题当前未修复：无事务包裹 + 提前 throw，错误计数与状态写入同时丢失。
- 排查“失败次数不增长”“验证失败后状态仍是 APPLY_20”类问题时，应首先怀疑本规则。

```ground:rule
name: 验证失败不落库
content: result=1/2 分支在 setErrorTryCount/setErrorTryTime 之后、saveOrUpdate 之前直接 throw，且方法无事务注解，错误次数与 APPLY_40 实际不会持久化
impact: 实现与设计不一致
field_targets:
  - cust_account_info.error_try_count
  - cust_account_info.error_try_time
  - cust_account_info.auth_state
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```