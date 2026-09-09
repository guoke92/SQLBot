---
type: caliber
title: 建档异常已存在口径
page_key: archive_exist_error
belong: calibers
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该口径定义下游返回消息包含“企业已建档”时，错误映射为标准业务错误码 REG_EXIST_EXCEPTION。

## 需求背景

将下游重复建档错误转换为统一规范错误码，便于调用方识别。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: 建档异常已存在口径
predicate: message CONTAINS '企业已建档' -> REG_EXIST_EXCEPTION 错误码
scope: AntArchiveErrorMapper.toResponse 异常映射
evidence: code_path:AntArchiveErrorMapper.toResponse
```

[[tables/AlipayAntArchiveResp]] [[rules/建档已存在错误识别]]