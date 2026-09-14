---
type: concept
title: 打款验证
page_key: payment_auth
domain: 企业银行账户
status: draft
aliases:
  - 小额打款
  - 打款认证
  - 打款验证码
oid: 1
scope:
  databases:
    - customer_management
sources:
  - db
  - code
contract_version: "0.1"
maps_to: cust_account_info.auth_state
field_targets:
  - cust_account_info.auth_state
also_confused_with:
  - cust_account_info.status
adjudication: boundary
belong: concepts
field_targets: [cust_account_info.auth_state]
sources: ["enrich:wiki-admin"]
---

# 打款验证

业务上指银行小额打款认证：向企业账户打入随机小额资金，由企业回填金额以确认账户可用。流程阶段落库在 `cust_account_info.auth_state`，取值见 [[auth_state]]，迁移见 [[bank_account_auth_state]]。

## 需求背景

账户验证受打款次数约束（[[payment_count_init]]、[[payment_count_exhausted]]）与金额区间约束（[[payment_amount_range]]）；验证失败的错误次数与状态存在不落库问题（[[verify_fail_not_persisted]]）。

## 版本演进

- 验证相关字段 `trans_id`（OriginalTxSN）、`trace_no` 由银行回写，用于后续查询与验证。
- `error_try_count`/`error_try_time` 在失败分支被设置，但因异常提前抛出且方法无事务注解，实际可能不持久化。

## 边界（adjudication: boundary）

`auth_state` 描述打款认证流程阶段（`APPLY_xx`）；`status` 是账户业务状态，DB 实测仅 `INIT`，代码无迁移。两者不可互推：账户“状态正常”不代表“打款已验证”。

相关：[[cust_account_info]]
