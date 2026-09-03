---
type: rule
title: 渠道固定为 ALIPAY_ANT
page_key: rule/channel_fixed_alipay_ant
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则强制将支付宝蚂蚁入站申请的渠道字段设置为 ALIPAY_ANT。

## 需求背景

所有经由支付宝蚂蚁渠道的建档申请必须标记为对应渠道，避免与其它渠道混淆。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 渠道固定为 ALIPAY_ANT
content: AlipayAntArchiveService.channelArchive 中执行 archiveReq.setChannel(AlipayAntCloudChannel.ALIPAY_ANT)
impact: 所有支付宝蚂蚁入站申请被标记为 ALIPAY_ANT 渠道
field_targets: ["channel"]
evidence: code_path:AlipayAntArchiveService.channelArchive
```

[[tables/ChannelArchiveReqDto]] [[channel_archive]]