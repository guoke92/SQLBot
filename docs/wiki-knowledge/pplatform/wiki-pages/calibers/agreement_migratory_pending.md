---
type: caliber
title: 协议迁移待拉取
page_key: agreement_migratory_pending
belong: calibers
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [argeement_migratory_record.status]
scope:
  databases: [lowcode_pplatform]
---

# 协议迁移待拉取

业务定位：用于标识尚未完成客户协议拉取的记录，是协议迁移重试机制的触发条件。

## 需求背景

当 `argeement_migratory_record.status = 'N'` 时，表示该协议尚未成功拉取，系统将尝试拉取并在失败时进行重试（`pull_num` 递增），超过上限或成功则置为 `Y`。该口径是重试逻辑的入口判断。

## 版本演进

暂无。

```ground:caliber
name: 协议迁移待拉取
predicate: argeement_migratory_record.status = 'N'
scope: 未完成客户协议拉取的记录
evidence: code:AgreementMigratoryService.pull
```

相关：[[argeement_migratory_record]]
