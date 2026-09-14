---
type: rule
title: 协议拉取任务节流
page_key: agreement_pull_throttle
domain: 租户迁移
status: draft
aliases: [协议拉取定时任务, 拉取节流]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:AgreementMigratoryService.java#AreementPullTask"
  - "code:AgreementMigratoryService.java#pull"
contract_version: "0.1"
belong: rules
---

单线程调度器每 30 秒执行一次，先抢 Redis 锁 `cust_argeement_pull` 再取 [[pending_agreement_pull]] 集合，按产品分组→按客户分组拉取；成功置 Y，失败 `pull_num+1` 保持 N。

```ground:rule
name: 协议拉取任务节流
content: "应用启动后由单线程调度器每 30 秒执行 pull()；Redis 锁 cust_argeement_pull；查询 status='N'/enable='Y'/pull_num<pullNum(默认20)，按产品分组→按客户分组拉取，成功写 status='Y'，失败 pull_num+1"
impact: "控制对业务系统协议接口的调用频次与重试"
field_targets:
  - argeement_migratory_record.status
  - argeement_migratory_record.pull_num
evidence: "code:AgreementMigratoryService.java#AreementPullTask"
```

## 需求背景

迁移协议量较大，需在不压垮业务系统接口的前提下逐步补齐，并保证多实例部署时同一批记录不被重复拉取。

## 版本演进

由启动即全量拉取演进为定时 + 分布式锁 + 限量重试；30 秒周期与 20 次上限均为当前默认值。

相关：[[argeement_migratory_record]]、[[agreement_pull_status]]。