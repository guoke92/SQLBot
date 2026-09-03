---
type: rule
title: reqSn 生成规则
page_key: rule/reqsn_generation_rule
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则定义同步请求流水号 reqSn 的生成逻辑：优先使用入参 reqNo，若为空则生成 UUID 并移除连字符。

## 需求背景

每次同步请求必须携带唯一流水号，确保请求可追溯。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: reqSn 生成规则
content: BaseClientSyncService.getReqSn 优先取入参 v.reqNo，若空则生成 UUID 并去除 '-'
impact: 保证每次同步请求有唯一流水号
field_targets: ["reqSn"]
evidence: code_path:BaseClientSyncService.getReqSn
```

[[serial_no]]