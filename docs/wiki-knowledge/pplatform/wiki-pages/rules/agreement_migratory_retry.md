---
type: rule
title: 协议迁移重试机制
page_key: agreement_migratory_retry
belong: rules
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [argeement_migratory_record.agreement_path, argeement_migratory_record.pull_num, argeement_migratory_record.status]
scope:
  databases: [lowcode_pplatform]
---

# 协议迁移重试机制

业务定位：保证协议迁移的可靠性与幂等性，失败后自动重试，成功或超过上限后终止。

## 需求背景

系统提供协议迁移能力（`AgreementMigratoryService.java:pull/doAgreement`）。待拉取的协议 `status=N`，拉取失败时 `pullNum+1`，超过上限或成功则置 `status=Y`；成功过滤空路径并保存合同。该规则与状态机 [[agreement_migratory_pull_status]] 直接关联。

## 版本演进

暂无。

```ground:rule
name: 协议迁移重试机制
content: 待拉取协议 status=N，拉取失败 pullNum+1，超过上限或成功置 status=Y；成功过滤空路径并保存合同
impact: 协议迁移可靠性与幂等控制
field_targets:
  - argeement_migratory_record.status
  - argeement_migratory_record.pull_num
  - argeement_migratory_record.agreement_path
evidence:
  - "code_path:AgreementMigratoryService.java:pull/updateAgreement/setAgreement"
  - "code_path:AgreementMigratoryService.java:pull/doAgreement + reqdoc:系统提供协议迁移能力"
```

相关：[[argeement_migratory_record]]
