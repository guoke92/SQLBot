---
type: caliber
title: 续费提醒窗口口径
page_key: renewal_reminder_window
belong: calibers
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.renew_remind_sent, ca_fee_company.service_end]
scope:
  databases: [lowcode_pplatform]
---

# 续费提醒窗口口径

业务定位：确定何时生成续费待办，即在服务到期前 7 天内且尚未生成过待办时触发。

## 需求背景

为避免服务中断，系统应在服务到期前提前提醒企业续费。该口径定义了触发条件，确保待办只生成一次。

## 版本演进

当前窗口为固定 7 天，未来可能支持配置化。

```ground:caliber
name: 续费提醒窗口口径
predicate: "ca_fee_company.service_end BETWEEN today AND today+7 AND ca_fee_company.renew_remind_sent='N'"
scope: 续费待办生成
evidence: "code:CaFeeScheduledJobHandler.doRenewalTodoJob + db:service_end"
```

[[ca_fee_company]] · [[renewal_reminder_window]]