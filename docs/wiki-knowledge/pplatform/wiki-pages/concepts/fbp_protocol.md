---
type: concept
title: FBP 接口协议
page_key: fbp_protocol
belong: concepts
domain: 支付宝蚂蚁档案与清算
status: published
aliases: ["FBP", "FbpReq", "FbpResp", "tradeCreditFundloanNotify"]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: fbp_protocol
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

FBP 是内部 RPC 调用协议，FbpReq 为请求体，FbpResp 为响应体。所有别名均指向同一协议体系。

## 需求背景

内部同步 RPC 调用采用 FBP 协议，请求与响应结构统一，确保跨服务通信规范。

## 版本演进

初始定义，暂无变更。边界说明来自语义分析 term_bridges。

[[tables/FbpReq]] [[tables/FbpResp]] [[rules/RPC 返回类型强校验]]