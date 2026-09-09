---
type: process
title: argeement_migratory_record.status
page_key: argeement_migratory_record_status
belong: processes
domain: 租户迁移
status: published
aliases: [协议迁移记录状态]
oid: 6
sources: [code_enum, code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：协议迁移记录状态机，表示协议拉取完成情况。

## 需求背景
协议拉取成功并保存合同后，状态由 N（待拉取/未完成）转为 Y（已完成）。

## 版本演进
v0.1 基于代码枚举与代码路径。

```ground:state_machine
field: argeement_migratory_record.status
states:
  - value: N
    label: 待拉取/未完成
    source: code_enum
  - value: Y
    label: 已完成
    source: code_enum
transitions:
  - from: N
    event: 协议拉取成功并保存合同
    to: Y
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/AgreementMigratoryService.java:setAgreement"
```

关联：[[agreement_record_idempotent]]