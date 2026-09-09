---
type: rule
title: 打款次数初始化
page_key: payment-count-init
belong: rules
domain: 企业银行账户与第三方银行
status: published
aliases: []
oid: 1
sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_account_info.payment_remaining_count, cust_setting_config.payment_maximum_number]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

规则“打款次数初始化”根据客户认证配置设置账户的剩余打款次数。该规则将配置值写入 `payment_remaining_count`。

## 需求背景

打款验证有次数上限，数据库需要记录剩余次数。该规则在 `updatePayCount` 方法中从配置读取 `paymentMaximumNumber`，控制打款申请上限。

## 版本演进

基于代码证据建立规则 v0。

```ground:rule
name: 打款次数初始化
content: 根据客户认证配置 paymentMaximumNumber 设置账户剩余打款次数 payment_remaining_count
impact: 控制打款验证申请上限
field_targets:
  - cust_account_info.payment_remaining_count
  - cust_setting_config.payment_maximum_number
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:updatePayCount"
```

[[cust_account_info]] 表字段 `payment_remaining_count` 参与该规则。

相关：[[cust_setting_config]]
