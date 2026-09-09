---
type: rule
title: 同步调用失败落库
page_key: sync_call_failure_persist
belong: rules
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则要求同步 RPC 调用失败时将失败信息写入 ClientApiSyncErrorDO，包括服务类名、参数 JSON、创建时间、启停标志（Y）与初始重试次数（1）。

## 需求背景

失败落库用于后续补偿或人工排查，是系统可靠性的重要保障。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 同步调用失败落库
content: BaseClientSyncService.error 方法将失败信息写入 ClientApiSyncErrorDO：serviceClassName、param(JSON)、createTime、enable=Y、retryNum=1
impact: 异步保存失败数据，供后续补偿或排查
field_targets: ["serviceClassName", "param", "retryNum", "enable"]
evidence: code_path:BaseClientSyncService.error
```

[[tables/ClientApiSyncErrorDO]] [[rules/同步 RPC 默认重试次数]]