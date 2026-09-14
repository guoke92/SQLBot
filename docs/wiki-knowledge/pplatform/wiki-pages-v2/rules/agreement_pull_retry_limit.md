---
type: rule
title: 协议迁移拉取的重试与上限
page_key: agreement_pull_retry_limit
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议拉取重试
  - pull_num 上限
oid: 1
scope:
  databases: [unknown]
sources:
  - code:AgreementMigratoryService.java
  - db:argeement_migratory_record
contract_version: "0.1"
belong: rules
---

协议迁移任务的调度与重试约束：定时执行 + Redis 锁防重；只取待拉取且有效的记录，失败则 `pull_num+1`，超过配置上限不再拉取。状态含义见 [[agreement_migratory_pending_pull]]、[[agreement_migratory_pulled]]、[[agreement_migratory_pull_status]]。

```ground:rule
name: 协议迁移拉取的重试与上限
content: "协议迁移任务每 30 秒执行，用 Redis 锁 cust_argeement_pull 防重；取 status=0 且 enable=Y、pull_num<配置值 的记录按产品/客户分组拉取，失败时 pull_num+1 后重试，超过上限不再拉取"
impact: "保证协议迁移的最终一致性与有限重试"
field_targets:
  - argeement_migratory_record.status
  - argeement_migratory_record.pull_num
  - argeement_migratory_record.enable
evidence: "code:AgreementMigratoryService.java:pull + AreementPullTask"
```