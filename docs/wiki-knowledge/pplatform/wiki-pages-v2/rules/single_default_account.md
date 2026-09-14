---
type: rule
title: 单企业唯一默认账户
page_key: single_default_account
domain: 企业银行账户
status: draft
aliases:
  - 默认账户互斥规则
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 单企业唯一默认账户

置默认时先把该企业已有 `default_account_flag='1'` 的账户改为 `'0'`，再把当前账户置 `'1'`，保证同一企业下仅一条默认。

## 需求背景

还款类业务只认唯一默认账户，口径见 [[default_repayment_account]]、术语见 [[default_account]]。

## 版本演进

- 由写时更新实现（先清后置），非数据库唯一索引；并发置默认时需确认是否互斥。

```ground:rule
name: 单企业唯一默认账户
content: 置默认时先把该企业已有 default_account_flag='1' 的账户改为 '0'，再把当前账户置 '1'
impact: 更新存量数据
field_targets:
  - cust_account_info.default_account_flag
evidence: code_path:CustAccountApplication.java:setDefaultFlag
```