---
type: rule
title: 蚂蚁建档流水号必填
page_key: rule/ant_archive_serial_no_required
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则要求蚂蚁建档入站请求必须携带非空外层流水号，否则抛出通用异常。

## 需求背景

流水号是建档请求的唯一标识，缺失将导致无法追踪和幂等处理。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 蚂蚁建档流水号必填
content: 在 AlipayAntArchiveService.channelArchive 中，若 outerSerialNo 为 blank，抛出 ApiValueObject.StatusCode.COMMON_EXCEPTION.e("流水号不能为空")
impact: 阻断建档入站，返回异常
field_targets: ["outerSerialNo"]
evidence: code_path:AlipayAntArchiveService.channelArchive
```

[[tables/ChannelArchiveReqDto]] [[serial_no]]