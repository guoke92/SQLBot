---
type: rule
title: 建档已存在错误识别
page_key: archive_exist_error_recognize
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

该规则识别下游建档重复错误，将包含“企业已建档”的消息映射为 REG_EXIST_EXCEPTION 错误码。

## 需求背景

重复建档是常见业务异常，需转为标准错误码返回给调用方。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 建档已存在错误识别
content: AntArchiveErrorMapper.toResponse 中，若 message 包含 '企业已建档'，返回 REG_EXIST_EXCEPTION 错误码
impact: 将下游建档重复错误映射为标准业务错误码
field_targets: ["code", "msg"]
evidence: code_path:AntArchiveErrorMapper.toResponse
```

[[tables/AlipayAntArchiveResp]] [[archive_exist_error]]