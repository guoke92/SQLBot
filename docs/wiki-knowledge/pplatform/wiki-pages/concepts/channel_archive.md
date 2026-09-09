---
type: concept
title: 渠道建档
page_key: channel_archive
belong: concepts
domain: 支付宝蚂蚁档案与清算
status: published
aliases: ["channelArchive", "蚂蚁建档", "支付宝蚂蚁建档"]
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
maps_to: channel_archive
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

渠道建档指支付宝蚂蚁渠道的企业建档入站流程。所有别名均指同一流程，渠道由请求体决定（固定 ALIPAY_ANT）。

## 需求背景

支付宝蚂蚁渠道需要建立企业档案，流程包含渠道标识、流水号处理、错误码映射等环节，统一术语有助于沟通。

## 版本演进

初始定义，暂无变更。边界说明来自语义分析 term_bridges。

[[tables/ChannelArchiveReqDto]] [[tables/ChannelArchiveRespDto]] [[rules/渠道固定为 ALIPAY_ANT]]