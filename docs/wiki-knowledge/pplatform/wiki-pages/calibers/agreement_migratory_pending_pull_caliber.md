---
type: caliber
title: "协议迁移待拉取口径"
page_key: agreement_migratory_pending_pull_caliber
belong: calibers
domain: "授权协议与电子授权"
status: published
aliases: ["待拉取协议口径", "迁移拉取条件口径"]
oid: 1

sources: ["code:AgreementMigratoryService.pull", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [argeement_migratory_record.enable, argeement_migratory_record.pull_num, argeement_migratory_record.status]
coverage_note: "记录级"
scope:
  databases: [lowcode_pplatform]
---

本口径筛选出需要执行拉取的协议迁移记录：记录有效、状态为待拉取、拉取次数未超上限。

## 需求背景

[[协议迁移记录状态机]] 的拉取动作基于该口径筛选记录。结合 [[协议迁移防重规则]] 防止重复拉取。

## 版本演进

暂无。

```ground:caliber
name: 协议迁移待拉取口径
predicate: "argeement_migratory_record.enable = 'Y' AND argeement_migratory_record.status = '0' AND argeement_migratory_record.pull_num < ${cust.agreemeent.pull.num}"
scope: "记录级"
evidence: "code:AgreementMigratoryService.pull"
```

相关：[[argeement_migratory_record]]
