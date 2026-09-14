---
type: rule
title: 协议文件落地与合同归档
page_key: agreement_file_contract_archive
domain: 租户迁移
status: draft
aliases: [协议归档, 文件落地 COS]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#createContractInfo"
  - "code:AgreementMigratoryService.java#agreementExist"
contract_version: "0.1"
belong: rules
---

拉取到的 `fileUrl` 先本地落地再上传 COS（PROJECT=FBP_SYSTEM），`path` 非空才 `migrateConctract` 写合同记录；同客户+同协议编号已存在则跳过，保证协议影像不重复、不丢。

```ground:rule
name: 协议文件落地与合同归档
content: "拉取到的 fileUrl 先本地落地再上传 COS（PROJECT=FBP_SYSTEM），path 非空才 migrateConctract 写入合同记录；已存在同 客户+合同编号 的跳过"
impact: "保证影像/协议不重复、不丢"
field_targets:
  - argeement_migratory_record.agreement_path
  - argeement_migratory_record.agreement_no
evidence: "code:AgreementMigratoryService.java#createContractInfo,#agreementExist"
```

## 需求背景

迁移期协议文件需与产融合同影像体系对齐，客户在产融侧查看合同时应能看到迁移之前的协议。

## 版本演进

由"拉取即写库"演进为先落地再上传 COS、并以客户+编号判重；`path` 为空时不再生成合同记录，避免脏数据。

相关：[[argeement_migratory_record]]、[[agreement_pull_status]]。