---
type: concept
title: 业务流水号
page_key: concept/serial_no
domain: 支付宝蚂蚁档案与清算
status: published
aliases: ["serialNo", "outerSerialNo", "reqNo"]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: serial_no
field_targets: []
adjudication: boundary
also_confused_with: ["businessNo"]
scope:
  databases: [lowcode_pplatform]
---

业务流水号用于标识渠道建档请求和同步 RPC 请求。serialNo/outerSerialNo 用于渠道建档请求标识；reqNo 用于同步 RPC 请求流水；businessNo 用于 FBP 业务号。各别名用途有边界，不可混用。

## 需求背景

渠道建档与同步 RPC 调用均需要唯一流水号追踪请求，清洗规则保证格式统一。

## 版本演进

初始定义，暂无变更。边界说明来自语义分析 term_bridges。

[[tables/ChannelArchiveReqDto]] [[rules/蚂蚁建档流水号必填]] [[rules/流水号去除首尾空白]]