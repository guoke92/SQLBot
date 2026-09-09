---
type: rule
title: RPC 响应 LocalDateTime 规范化
page_key: rpc_localdatetime_normalize
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

该规则定义对 Dubbo 泛化调用返回的 {date,time} 嵌套结构进行递归转换，统一为标准 LocalDateTime。

## 需求背景

解决泛化调用时间字段反序列化问题，确保时间数据可用。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: RPC 响应 LocalDateTime 规范化
content: BaseClientSyncService.normalizeLocalDateTimeFields 递归将 Dubbo 泛化返回的 {date,time} 嵌套结构转换为标准 LocalDateTime
impact: 解决泛化调用时间字段反序列化问题
field_targets: ["LocalDateTime"]
evidence: code_path:BaseClientSyncService.normalizeLocalDateTimeFields
```

[[fbp_protocol]]