---
type: caliber
title: 协议迁移有效记录
page_key: agreement_migratory_enabled
domain: 授权协议与电子授权
status: draft
aliases:
  - enable=Y
  - 协议拉取有效记录
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
belong: calibers
---

协议拉取一律附带的有效性过滤条件，与 [[authorization_agreement]] 中的 `enable` 语义一致（逻辑启用标识）。当前 DB 中该表 `enable` 全为 Y、无 N，因此该口径目前不产生过滤效果，但属于取数必经条件，见 [[agreement_migratory_pending_pull]]。

```ground:caliber
name: 协议迁移有效记录
predicate: "argeement_migratory_record.enable = 'Y'"
scope: "协议拉取一律过滤 enable=Y（DB 中全为 Y，无 N）"
evidence: "code:AgreementMigratoryService.java:pull + db"
```