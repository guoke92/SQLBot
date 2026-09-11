---
type: caliber
title: 待拉取协议记录
page_key: caliber.pending_pull_agreement_records
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议拉取扫描口径
  - pull 捞取条件
oid: 1
scope:
  databases: [unknown]
sources:
  - code:AgreementMigratoryService.java
  - db:argeement_migratory_record
contract_version: "0.1"
---

定时任务捞取待拉取记录的条件是「未结束 + 有效 + 未超重试上限」：`status='0'`、`enable='Y'`、`pull_num < 20`（20 为配置 `cust.agreemeent.pull.num` 默认值）。失败一次 `pull_num` 自增 1，因此记录在有限次尝试后自然退出扫描集合。状态语义见 [[processes/agreement-migratory-pull-status]]，字段释义见 [[tables/argeement_migratory_record]]。

## 需求背景
客户端可能长期无法返回某类协议，若无限重试会持续占用定时任务容量；用次数上限把「一直失败」的记录自然淘汰，同时用 `status` 终态区分「已确认无此协议」。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 待拉取协议记录
predicate: "argeement_migratory_record.status = '0' AND argeement_migratory_record.enable = 'Y' AND argeement_migratory_record.pull_num < 20"
scope: "协议拉取定时任务（20 为 cust.agreemeent.pull.num 默认值）"
evidence: "code_path:AgreementMigratoryService.java#pull"
```