---
type: rule
title: 续费提醒与到期规则
page_key: renewal_remind_expire
domain: CA证书收费
status: draft
aliases:
  - 续费待办
  - 服务到期
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeScheduledJobHandler.java
  - code_path:CaFeeRenewalService.java
contract_version: "0.1"
belong: rules
---

`service_end` 剩余 ≤7 天且 `renew_remind_sent=N` 时生成续费待办；`service_end < today` 时完结「即将到期」待办、关闭 `RENEW` 待缴单、企业 `pay_status` 置 `UNPAID`，并按需创建 `RENEW_EXPIRED` 订单并发已过期待办。相关口径见 [[order_status_closed]]、[[company_pay_status_unpaid]]，状态机见 [[ca_fee_company_pay_status]]。

## 需求背景

续费是收费模型的持续收入来源：需要在到期前提醒、到期后刷新企业状态并生成补缴入口，同时避免旧待缴单与新周期订单并存。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 续费提醒与到期规则
content: service_end 剩余≤7天且 renew_remind_sent=N 时生成续费待办；service_end<today 时完结即将到期待办、关闭 RENEW 待缴单、企业 pay_status 置 UNPAID，并按需创建 RENEW_EXPIRED 订单发已过期待办
impact: 到期续费提醒和服务状态刷新
field_targets:
  - ca_fee_company.service_end
  - ca_fee_company.renew_remind_sent
  - ca_fee_company.pay_status
  - ca_fee_order.order_type
evidence: CaFeeScheduledJobHandler + CaFeeRenewalService
```