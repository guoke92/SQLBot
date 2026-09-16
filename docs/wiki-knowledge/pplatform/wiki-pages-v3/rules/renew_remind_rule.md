---
type: rule
title: 续费提醒规则
page_key: renew_remind_rule
domain: CA证书收费
status: draft
aliases: [caFeeRenewalTodoJob]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeScheduledJobHandler.java:caFeeRenewalTodoJob"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - ca_fee_company.service_end
  - ca_fee_company.renew_remind_sent
---

触发集合即口径 [[expiring_soon]]。命中后生成 RENEW 待缴订单、发续费待办，并把 [[ca_fee_company]] 的 `renew_remind_sent` 置 Y。同一服务期只发一次；到期处理后复位见 [[ca_fee_renew_remind]]。

```ground:rule
name: 续费提醒规则
content: 企业 service_end 距今 ≤7 天且 renew_remind_sent='N' 时，生成 RENEW 待缴订单并发送续费待办，随后置 renew_remind_sent='Y'。
impact: 触发续费订单和提醒。
field_targets: [ca_fee_company.service_end, ca_fee_company.renew_remind_sent]
evidence: "code_path:CaFeeScheduledJobHandler.java:caFeeRenewalTodoJob"
```
