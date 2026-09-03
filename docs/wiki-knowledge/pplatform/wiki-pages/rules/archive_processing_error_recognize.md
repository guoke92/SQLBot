---
type: rule
title: 建档处理中错误识别
page_key: rule/archive_processing_error_recognize
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则识别下游建档处理中错误，将包含“建档处理中”的消息映射为 COMMON_EXCEPTION 错误码。

## 需求背景

处理中状态需要以通用异常码告知调用方操作未完成。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 建档处理中错误识别
content: AntArchiveErrorMapper.toResponse 中，若 message 包含 '建档处理中'，返回 COMMON_EXCEPTION 错误码
impact: 将处理中错误映射为通用异常
field_targets: ["code", "msg"]
evidence: code_path:AntArchiveErrorMapper.toResponse
```

[[tables/AlipayAntArchiveResp]] [[archive_processing_error]]