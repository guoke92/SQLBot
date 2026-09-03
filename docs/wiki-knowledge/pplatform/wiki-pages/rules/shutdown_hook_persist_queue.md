---
type: rule
title: 关闭钩子保存队列未处理数据
page_key: rule/shutdown_hook_persist_queue
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则要求服务关闭时遍历阻塞队列，将未处理数据通过 error 方法落库，异常标记为程序重启或异常停止。

## 需求背景

避免服务停机导致队列中数据丢失，保证数据最终可补偿。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 关闭钩子保存队列未处理数据
content: BaseClientSyncService.shutdownExecutor 遍历阻塞队列，将未处理数据调用 error 落库，异常标记为程序重启或异常停止
impact: 避免服务停机丢失队列数据
field_targets: ["queue"]
evidence: code_path:BaseClientSyncService.shutdownExecutor
```

[[rules/同步调用失败落库]]