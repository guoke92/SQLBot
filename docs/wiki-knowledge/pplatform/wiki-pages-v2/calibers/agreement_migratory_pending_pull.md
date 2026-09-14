---
type: caliber
title: 待拉取协议记录
page_key: agreement_migratory_pending_pull
domain: 授权协议与电子授权
status: draft
aliases:
  - status=0
  - 待拉取口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
belong: calibers
---

协议迁移拉取任务的取数口径。实际取数不是单条件，而是复合条件：`status='0'` 且 `enable='Y'` 且 `pull_num < 配置值`，见 [[agreement_migratory_enabled]] 与 [[agreement_pull_retry_limit]]；状态推进见 [[agreement_migratory_pull_status]]。

```ground:caliber
name: 待拉取协议记录
predicate: "argeement_migratory_record.status = '0'"
scope: "协议迁移拉取任务取数（复合条件 enable='Y' AND pull_num<配置值）"
evidence: "code:AgreementMigratoryService.java:pull + db"
```