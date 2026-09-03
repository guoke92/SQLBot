---
type: concept
title: 端类型
page_key: concept_client_type
domain: 企业变更与运营变更
status: published
aliases: ["clientType"]
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_change_cfg.client_type"
field_targets: ["cust_change_cfg.client_type"]
adjudication: "synonym"
also_confused_with: []
coverage_note: 术语边界
scope:
  databases: [lowcode_pplatform]
---

“端类型”标识发起变更的客户端类型，由 `WebUserUtil.getClientType()` 获取，用于变更配置查询时匹配客户端环境。

## 需求背景

暂无额外边界说明。

## 版本演进

暂无。

相关：[[cust_change_cfg]]
