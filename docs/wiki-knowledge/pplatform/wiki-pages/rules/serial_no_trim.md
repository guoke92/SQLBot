---
type: rule
title: 流水号去除首尾空白
page_key: rule/serial_no_trim
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则要求对建档请求中的外层流水号执行 trim 操作，去除首尾空白后写入 serialNo 字段。

## 需求背景

用户输入或上游传递的流水号可能包含不可见空白字符，统一去除可避免后续匹配异常。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 流水号去除首尾空白
content: archiveReq.setSerialNo(outerSerialNo.trim())
impact: 统一流水号格式，避免空白字符干扰
field_targets: ["serialNo"]
evidence: code_path:AlipayAntArchiveService.channelArchive
```

[[tables/ChannelArchiveReqDto]] [[serial_no]]