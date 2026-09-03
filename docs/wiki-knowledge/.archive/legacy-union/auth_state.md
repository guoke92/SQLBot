---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-product-activation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 银行账户认证状态
page_key: auth_state
domain: 客户与建档
aliases:
- 小额打款
- 账户验证
- 打款认证
- 打款验证
- 账户认证进度
- 银行账户验证
anchors:
- auth_state
---
# 银行账户认证状态

cust_account_info.auth_state 六值枚举（APPLY_00~50），其中 APPLY_00/APPLY_50 全仓无写点（死值）：APPLY_10 申请受理（cnapsPaymentApply，payment_remaining_count-1）→ APPLY_20/30 打款成功/失败（银行查询映射）→ APPLY_40 验证终态（result=0 成功；result=1/2 失败且 error_try_count+1）。APPLY_40 兼容成功与失败，判成败须看 error_try_count。

```ground:enum
enum: auth_state
fields:
- cust_account_info.auth_state
values:
  APPLY_00:
    label: 初始化
  APPLY_10:
    label: 申请受理中
  APPLY_20:
    label: 受付打款成功
  APPLY_30:
    label: 打款失败
  APPLY_40:
    label: 验证完成（成功/失败终态）
  APPLY_50:
    label: 验证失败
```

## 关联
- [[cust_account_info|cust_account_info]]
