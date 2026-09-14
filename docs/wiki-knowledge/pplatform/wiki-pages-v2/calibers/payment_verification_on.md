---
type: caliber
title: 打款验证开启
page_key: payment_verification_on
domain: notification
status: draft
aliases: [paymentVerification=yes 口径]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config.payment_verification
contract_version: "0.1"
belong: calibers
---

payment_verification='yes' 表示该企业启用打款验证，认证时可通过向企业对公账户打款并回填金额完成验证。最多申请次数由 payment_maximum_number 控制。

## 需求背景
打款验证用于在无人值守场景下替代人工审核，需求侧要求企业可自行开启。

## 版本演进
- 仅 DB 样本支撑；打款次数上限字段当前无代码消费证据。

```ground:caliber
name: 打款验证开启
predicate: cust_setting_config.payment_verification = 'yes'
scope: 企业认证配置
evidence: db
```