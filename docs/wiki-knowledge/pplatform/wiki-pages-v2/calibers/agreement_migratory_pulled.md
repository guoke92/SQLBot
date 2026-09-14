---
type: caliber
title: 已拉取协议记录
page_key: agreement_migratory_pulled
domain: 授权协议与电子授权
status: draft
aliases:
  - status=1
  - 已拉取口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
belong: calibers
---

协议迁移的终态口径。注意“已拉取完成”并不必然意味着存在协议文件：客户端返回空协议集时会被标记为已完成，`agreement_path` 可能为空，见 [[agreement_migratory_pull_status]]。

```ground:caliber
name: 已拉取协议记录
predicate: "argeement_migratory_record.status = '1'"
scope: "迁移协议拉取结果终态"
evidence: "code + db"
```