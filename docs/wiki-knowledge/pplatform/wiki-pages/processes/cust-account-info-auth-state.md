---
type: process
title: cust_account_info.auth_state 小额打款验证认证状态机
page_key: cust-account-info-auth-state
belong: processes
domain: 企业银行账户与第三方银行
status: published
aliases: ["auth_state状态机", "小额打款验证状态机"]
oid: 1
sources: ["db", "code"]
contract_version: "0.1"
field_targets: [cust_account_info.auth_state]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

该状态机描述 `cust_account_info.auth_state` 字段在小额打款验证场景下的状态流转。状态从初始 `APPLY_00` 开始，通过申请、查询、确认等事件推进至终态 `APPLY_40`。

## 需求背景

小额打款验证要求企业提供对公账户，银行向该账户打入随机小额金额，企业回填金额完成验证。系统通过申请、查询受理结果、用户确认等步骤驱动账户认证状态变化。该状态机将代码中的状态转换行为固化为契约。

## 版本演进

基于 `CustAccountApplication.java` 中的方法调用建立状态机 v0。当前覆盖申请、查询、确认与重新申请路径。

```ground:process
name: cust_account_info.auth_state 小额打款验证认证状态机
field: auth_state
states:
  - value: APPLY_00
    label: 初始状态/未申请打款
    source: db_dist
  - value: APPLY_10
    label: 已申请打款/银行未受理成功
    source: code_enum
  - value: APPLY_20
    label: 银行受理成功/待用户确认金额
    source: db_dist
  - value: APPLY_30
    label: 申请打款受理失败
    source: code_enum
  - value: APPLY_40
    label: 验证完成/已验证通过或验证失败终态
    source: db_dist
transitions:
  - from: APPLY_00
    event: cnapsPaymentApply 申请打款
    to: APPLY_10
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply"
  - from: APPLY_10
    event: paymentResult 查询申请结果 status=10
    to: APPLY_10
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult"
  - from: APPLY_10
    event: paymentResult 查询申请结果 status=20
    to: APPLY_20
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult"
  - from: APPLY_10
    event: paymentResult 查询申请结果 status=30
    to: APPLY_30
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult"
  - from: APPLY_20
    event: cnapsPaymentConfirm 打款验证确认 result=0/1/2
    to: APPLY_40
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm"
  - from: APPLY_30
    event: cnapsPaymentApply 重新申请打款
    to: APPLY_10
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply"
```

[[cust_account_info]] 表字段 `auth_state` 承载该状态机。