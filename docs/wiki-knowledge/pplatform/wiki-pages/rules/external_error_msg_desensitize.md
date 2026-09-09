---
type: rule
title: 外部错误消息脱敏
page_key: external_error_msg_desensitize
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

该规则要求当消息以 CA_CERT_ 开头且包含冒号时，仅返回冒号后内容，否则返回完整消息。目的是对外隐藏内部异常前缀。

## 需求背景

内部错误消息包含技术细节，需脱敏后返回给调用方，只暴露可读业务信息。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 外部错误消息脱敏
content: AntArchiveErrorMapper.extractOutwardMsg 中，若消息以 CA_CERT_ 开头且包含冒号，仅返回冒号后内容；否则返回原消息
impact: 对外隐藏内部异常前缀，仅暴露可读信息
field_targets: ["msg"]
evidence: code_path:AntArchiveErrorMapper.extractOutwardMsg
```

[[tables/AlipayAntArchiveResp]] [[rules/CA 证书错误码显式映射]]