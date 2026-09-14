---
type: caliber
title: 待拉取协议集合
page_key: pending_agreement_pull
domain: 租户迁移
status: draft
aliases: [待拉取协议口径, status=N 协议集合]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#pull"
contract_version: "0.1"
belong: calibers
---

本口径决定"这一轮要去业务系统拉哪些协议"，是一个多条件叠加的集合，不是简单单项过滤：状态为 N 只是必要条件，还需 enable='Y'、未超过重试上限、且不属于排除产品。口径实现见 [[agreement_pull_throttle]]，状态流转见 [[agreement_pull_status]]。

```ground:caliber
name: 待拉取协议集合
predicate: "argeement_migratory_record.status = 'N'"
scope: "协议拉取定时任务 pull()：叠加 enable='Y'、pull_num < pullNum(默认20)、排除 excludeProductCode 产品"
evidence: "code:AgreementMigratoryService.java#pull"
```

## 需求背景

迁移协议需要按产品分批、按客户分组回捞，控制对业务系统接口的调用频次；被排除的产品在迁移期不应产生拉取流量。

## 版本演进

过滤条件由 status 单项演进为四项叠加；`pullNum` 默认 20 作为失败退出阈值，达到上限后记录保持 N 但不再被选中（属人工介入场景）。