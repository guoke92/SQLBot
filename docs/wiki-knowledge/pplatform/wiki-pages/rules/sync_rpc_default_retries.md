---
type: rule
title: 同步 RPC 默认重试次数
page_key: sync_rpc_default_retries
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

该规则定义同步 RPC 调用失败时最大重试次数为 3，由配置项 sync.rpc.retries 控制，默认值 3。

## 需求背景

RPC 调用可能因网络抖动失败，重试机制提升成功率，但需限制次数避免无限重试。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 同步 RPC 默认重试次数
content: BaseClientSyncService 使用 @NacosValue(value = "${sync.rpc.retries:3}") 注入重试次数，默认 3
impact: RPC 调用失败最多重试 3 次
field_targets: ["retries"]
evidence: code_path:BaseClientSyncService.retries
```

[[rules/同步调用失败落库]]