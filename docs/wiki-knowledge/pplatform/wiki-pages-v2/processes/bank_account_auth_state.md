---
type: process
title: 银行账户打款认证状态
page_key: bank_account_auth_state
domain: 企业银行账户
status: draft
aliases:
  - 打款认证状态机
  - auth_state 状态机
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
belong: processes
---

# 银行账户打款认证状态

`cust_account_info.auth_state` 的生命周期：初始 `APPLY_00` → 发起小额打款申请进入 `APPLY_10` → 银行受理成功 `APPLY_20`（或受理失败 `APPLY_30`）→ 验证金额一致落 `APPLY_40`。字段枚举见 [[auth_state]]，业务术语见 [[payment_auth]]。

## 需求背景

账户须通过银行小额打款验证方可确认可用：申请前受打款次数约束（[[payment_count_exhausted]]、[[payment_count_init]]），验证金额受区间校验（[[payment_amount_range]]），验证失败分支存在不落库问题（[[verify_fail_not_persisted]]）。初始态口径见 [[not_applied_payment_auth]]。

## 版本演进

- `APPLY_00`（DB 列默认）与 `APPLY_20`/`APPLY_40` 出现在生产数据；`APPLY_10`/`APPLY_30` 见于代码常量。
- 查询打款结果 `status=10` 时幂等重写为 `APPLY_10`。
- `result=1/2` 两条迁移指向 `APPLY_40`，但实现中先抛异常、状态不落库，迁移实际不成立。

```ground:process
name: 银行账户打款认证状态
field: cust_account_info.auth_state
states:
  - value: APPLY_00
    label: 初始，未发起打款认证（DB 列默认值）
    source: db_dist
  - value: APPLY_10
    label: 已提交打款申请、待银行受理
    source: code_const
  - value: APPLY_20
    label: 银行受理成功（允许发起金额验证）
    source: code_const
  - value: APPLY_30
    label: 申请打款受理失败
    source: code_const
  - value: APPLY_40
    label: 已完成验证（金额一致时落库）
    source: db_dist
transitions:
  - from: APPLY_00
    event: 发起小额打款申请 cnapsPaymentApply
    to: APPLY_10
    evidence: code_path:CustAccountApplication.java:193
  - from: APPLY_10
    event: 查询打款结果 status=10（幂等重写）
    to: APPLY_10
    evidence: code_path:CustAccountApplication.java:222
  - from: APPLY_10
    event: 查询打款结果 status=20
    to: APPLY_20
    evidence: code_path:CustAccountApplication.java:224
  - from: APPLY_10
    event: 查询打款结果 status=30
    to: APPLY_30
    evidence: code_path:CustAccountApplication.java:226
  - from: APPLY_20
    event: 打款验证金额一致 result=0
    to: APPLY_40
    evidence: code_path:CustAccountApplication.java:283
  - from: APPLY_20
    event: 打款验证金额不匹配 result=1（抛异常，状态未落库）
    to: APPLY_40
    evidence: code_path:CustAccountApplication.java:287
  - from: APPLY_20
    event: 银行库无记录 result=2（抛异常，状态未落库）
    to: APPLY_40
    evidence: code_path:CustAccountApplication.java:293
```