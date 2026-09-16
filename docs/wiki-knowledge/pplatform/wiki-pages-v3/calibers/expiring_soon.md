---
type: caliber
title: 即将到期待提醒
page_key: expiring_soon
domain: CA证书收费
status: draft
aliases: [7天内到期]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeScheduledJobHandler.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - ca_fee_company.service_end
  - ca_fee_company.renew_remind_sent
---

续费待办工作队列，列在 [[ca_fee_company]]：当前服务期 7 天内到期，且本期还没生成提醒。已提醒企业会退出本口径（[[ca_fee_renew_remind]]）。统计「所有 7 天内到期」时不要带 `renew_remind_sent='N'`。

```ground:caliber
name: 即将到期待提醒
predicate: "ca_fee_company.service_end <= DATE_ADD(CURDATE(), INTERVAL 7 DAY) AND ca_fee_company.renew_remind_sent = 'N'"
scope: ca_fee_company
evidence: code
```
