---
type: process
title: 续费提醒发送闸
page_key: ca_fee_renew_remind
domain: CA证书收费
status: draft
aliases: [renew_remind_sent]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeRenewalService.java", "code:CaFeeCompanyDO.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [ca_fee_company.renew_remind_sent]
---

作用于 [[ca_fee_company]] 的 `renew_remind_sent`（Y/N，字典仍是 [[enable]]）。字段注释：Y 已生成 / N 未生成。只表示**当前服务期**是否已生成续费待办；`markServiceExpired` 会从 Y 复位为 N，下一周期可再发。

触发条件见 [[renew_remind_rule]] / [[expiring_soon]]。

```ground:process
name: 续费提醒发送闸
field: ca_fee_company.renew_remind_sent
states:
  - value: N
    label: 未生成
    source: code_comment
  - value: Y
    label: 已生成
    source: code_comment
transitions:
  - from: N
    event: 续费待办生成 markRenewRemindSent
    to: Y
    evidence: "code_path:CaFeeRenewalService.java:markRenewRemindSent"
  - from: Y
    event: 服务到期处理 markServiceExpired
    to: N
    evidence: "code_path:CaFeeRenewalService.java:markServiceExpired"
```
