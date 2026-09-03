---
type: caliber
title: 建档处理中口径
page_key: caliber/archive_processing_error
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该口径定义下游返回消息包含“建档处理中”时，错误映射为通用异常错误码 COMMON_EXCEPTION。

## 需求背景

处理中状态需告知调用方当前操作未完成，采用通用异常码表达。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: 建档处理中口径
predicate: message CONTAINS '建档处理中' -> COMMON_EXCEPTION 错误码
scope: AntArchiveErrorMapper.toResponse 异常映射
evidence: code_path:AntArchiveErrorMapper.toResponse
```

[[tables/AlipayAntArchiveResp]] [[rules/建档处理中错误识别]]