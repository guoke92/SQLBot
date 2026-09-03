---
type: rule
title: 续费提醒窗口
page_key: renewal_reminder_window
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.renew_remind_sent, ca_fee_order.order_type]
scope:
  databases: [lowcode_pplatform]
---

# 续费提醒窗口

业务定位：定义生成续费待办的触发规则，确保在服务到期前及时提醒企业。

## 需求背景

为避免服务中断，系统在服务到期前 7 天且尚未生成待办时，自动生成 RENEW 类型待办，提醒企业续费。

## 版本演进

窗口固定为 7 天，未来可能支持配置化或分级提醒。

```ground:rule
name: 续费提醒窗口
content: 剩余≤7天且 renew_remind_sent=N 时生成 RENEW 待办
impact: 提前提醒续费
field_targets: ["ca_fee_company.renew_remind_sent", "ca_fee_order.order_type"]
evidence: code:CaFeeScheduledJobHandler.caFeeRenewalTodoJob
```

[[renewal_reminder_window]] · [[ca_fee_company]] · [[ca_fee_order]]