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
type: rule
title: auth_state 死值警告
page_key: auth_state-死值警告
domain: 客户与建档
field_targets:
- cust_account_info.auth_state
- cust_account_info.error_try_count
---
# auth_state 死值警告

APPLY_00（初始化）与 APPLY_50（验证失败）在当前代码中无写点；APPLY_40 同时承接验证成功（result=0）与失败（result=1/2），判成败必须联合 error_try_count>0。

```ground:rule
rule: auth-state-dead-values
field_targets:
- cust_account_info.auth_state
- cust_account_info.error_try_count
impact: query_constraint
content: APPLY_00（初始化）与 APPLY_50（验证失败）在当前代码中无写点；APPLY_40 同时承接验证成功（result=0）与失败（result=1/2），判成败必须联合
  error_try_count>0。
scope: 按认证状态统计账户
```

## 关联
- [[cust_account_info]]
