---
type: process
title: 协议迁移拉取状态
page_key: agreement_migratory_pull_status
belong: processes
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code_enum"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 协议迁移拉取状态

业务定位：描述客户协议从“待拉取”到“已完成”的状态变化，保证协议迁移的可靠性与幂等性。

## 需求背景

协议迁移过程中，`status` 初始为 `N` 表示待拉取，当拉取协议成功并保存后，状态更新为 `Y`。若拉取失败则进行重试，超过上限或成功均会置为 `Y`。该状态机是协议迁移重试机制的核心。

## 版本演进

暂无。

```ground:process
name: 协议迁移拉取状态
field: status
states:
  - value: N
    label: 待拉取
    source: code_enum
  - value: Y
    label: 已完成
    source: code_enum
transitions:
  - from: N
    event: 拉取协议成功并保存
    to: Y
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/AgreementMigratoryService.java:updateAgreement
```