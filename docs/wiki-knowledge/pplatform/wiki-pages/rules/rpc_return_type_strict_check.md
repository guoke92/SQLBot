---
type: rule
title: RPC 返回类型强校验
page_key: rpc_return_type_strict_check
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

该规则要求同步 RPC 调用返回对象的类名必须为 FbpResp.class.getName()，否则抛出 IllegalArgumentException。

## 需求背景

确保 RPC 响应符合 FBP 协议约定，避免解析异常或类型转换错误。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: RPC 返回类型强校验
content: 在 BaseClientSyncService.loop 中，若返回对象解析后 class 不是 FbpResp.class.getName()，抛出 IllegalArgumentException("返回未定义的结果")
impact: 确保 RPC 响应符合 FBP 协议，否则视为失败
field_targets: ["data"]
evidence: code_path:BaseClientSyncService.loop
```

[[tables/FbpReq]] [[tables/FbpResp]] [[fbp_protocol]]