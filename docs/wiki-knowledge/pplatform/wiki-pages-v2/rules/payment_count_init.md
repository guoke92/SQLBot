---
type: rule
title: 打款次数初始化
page_key: payment_count_init
domain: 企业银行账户
status: draft
aliases:
  - payment_remaining_count 初始化规则
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 打款次数初始化

从 `cust_setting_config.payment_maximum_number` 取首条配置，写入账户的 `payment_remaining_count`，作为该账户可发起打款次数的起点。

## 需求背景

打款验证的调用次数需要受控，次数上限走配置而非硬编码，见 [[payment_auth]]、[[payment_count_exhausted]]。

## 版本演进

- 取“首条配置”意味着配置表存在多条时以第一条为准，后续若配置分租户/分渠道，需要重新确认取数逻辑。

```ground:rule
name: 打款次数初始化
content: 从 cust_setting_config.payment_maximum_number 取首条配置写入 payment_remaining_count
impact: 初始化字段
field_targets:
  - cust_account_info.payment_remaining_count
  - cust_setting_config.payment_maximum_number
evidence: code_path:CustAccountApplication.java:updatePayCount
```