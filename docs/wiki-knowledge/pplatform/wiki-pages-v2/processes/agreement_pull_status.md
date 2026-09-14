---
type: process
title: 迁移协议拉取状态机
page_key: agreement_pull_status
domain: 租户迁移
status: draft
aliases: [协议拉取状态机, argeement_migratory_record.status 状态机]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#pull"
  - "code:AgreementMigratoryService.java#updateAgreement"
  - "code:AgreementMigratoryService.java#updateAgreementPullNum"
  - "code:AgreementMigratoryService.java#syncAgreementDoc"
  - "db:argeement_migratory_record"
contract_version: "0.1"
belong: processes
---

协议记录的拉取状态机：N 是待办，Y 是终态（拉到、或确认业务系统没有、或已通过推送同步补齐）。N 状态允许通过 `pull_num` 累加多次重试，直到达到上限（默认 20）。相关：[[pending_agreement_pull]]、[[agreement_pull_throttle]]、[[agreement_file_contract_archive]]。

```ground:process
name: 迁移协议拉取状态
field: argeement_migratory_record.status
states:
  - value: N
    label: "待拉取（BooleanEnum.no）"
    source: code_enum
  - value: Y
    label: "已拉取完成 / 客户端确认无该协议"
    source: code_enum
transitions:
  - from: N
    event: "定时任务 pull() 按产品+客户分组拉取到协议并写回"
    to: Y
    evidence: "code_path:AgreementMigratoryService.java#updateAgreement"
  - from: N
    event: "拉取失败（pull_num+1，状态保持 N，等待下一轮）"
    to: N
    evidence: "code_path:AgreementMigratoryService.java#updateAgreementPullNum"
  - from: N
    event: "协议推送同步 syncAgreementDoc"
    to: Y
    evidence: "code_path:AgreementMigratoryService.java#syncAgreementDoc"
```

## 需求背景

迁移时只登记"待拉取清单"，协议文件在迁移后按批补拉并归档；业务系统明确无该协议时也必须能置为完成，避免清单永久滞留。

## 版本演进

重试由无限重试收敛为 `pull_num < pullNum(默认20)` 节流；状态机的出口从"仅拉取成功"扩展出"客户端确认无协议"与"推送同步"两条完成路径。