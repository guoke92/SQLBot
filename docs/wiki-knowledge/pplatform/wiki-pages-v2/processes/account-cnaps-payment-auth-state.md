---
type: process
title: 银行账户小额打款认证状态机
page_key: processes/account-cnaps-payment-auth-state
domain: 企业银行账户
status: draft
aliases: [CNAPS 打款认证流程, auth_state 状态机]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java
contract_version: "0.1"
---

本流程描述企业银行账户（[[tables/cust_account_info]]）通过人行小额打款完成真实性认证的完整状态流转：申请打款 → 银行受理 → 金额验证。字段 `auth_state` 的五态取值与迁移条件是账户认证能力的核心契约，被 [[calibers/account-payment-auth-passed]]、[[rules/payment-confirm-precondition]]、[[rules/payment-fail-count]] 直接引用。

## 需求背景

账户真实性无法在录入时判断，必须由银行侧发起一笔小额打款、企业侧回填收到的金额来验证账户可用。因此系统需要记录「是否已发起」「银行是否受理」「验证结果」三类事实，并对验证动作施加时序约束（未申请不能验、未受理不能验、受理失败需重新申请）。剩余次数与失败次数用于限制试探，见 [[rules/payment-count-quota]]；金额范围与单位换算见 [[rules/payment-amount-range]]；打款交易标识的取值来源见 [[concepts/trans-id-vs-trace-no]]。

## 版本演进

v0 契约按现状固化，五态基线来自代码枚举。需注意两处与直觉不一致的现行行为：(1) 银行受理失败后可无前置状态校验地直接重新申请，属于覆盖式回退；(2) 金额不匹配或银行库无记录时同样落 APPLY_40 并累加失败次数后抛异常，故 APPLY_40 不能单独作为「验证通过」口径。

## 状态与迁移锚点

```ground:state_machine
name: 银行账户小额打款认证状态机
field: cust_account_info.auth_state
states:
  - value: APPLY_00
    label: 初始/未发起打款
    source: code_enum
  - value: APPLY_10
    label: 打款申请已提交，银行受理中
    source: code_enum
  - value: APPLY_20
    label: 银行受理成功，可进行金额验证
    source: code_enum
  - value: APPLY_30
    label: 申请打款受理失败，需重新申请
    source: code_enum
  - value: APPLY_40
    label: 已完成打款验证（金额一致，或验证不匹配/库无记录时也落该值）
    source: code_enum
transitions:
  - from: APPLY_00
    event: 申请打款 cnapsPaymentApply()
    to: APPLY_10
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply
  - from: APPLY_10
    event: 查询打款结果 paymentResult() 返回 status=20
    to: APPLY_20
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult
  - from: APPLY_10
    event: 查询打款结果 paymentResult() 返回 status=30
    to: APPLY_30
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult
  - from: APPLY_20
    event: 打款验证 cnapsPaymentConfirm() 金额一致 result=0
    to: APPLY_40
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm
  - from: APPLY_20
    event: 打款验证 cnapsPaymentConfirm() 金额不匹配/库无记录 result=1|2（同时 error_try_count+1、error_try_time=now 后抛业务异常）
    to: APPLY_40
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm
  - from: APPLY_30
    event: 重新申请打款 cnapsPaymentApply()（无前置状态校验，直接覆盖）
    to: APPLY_10
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply
```