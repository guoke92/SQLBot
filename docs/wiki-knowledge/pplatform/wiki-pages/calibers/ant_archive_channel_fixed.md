---
type: caliber
title: 蚂蚁建档渠道固定
page_key: ant_archive_channel_fixed
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

该口径规定支付宝蚂蚁建档入站服务中渠道字段固定为 ALIPAY_ANT，不随请求变化。

## 需求背景

确保所有入站申请被正确标记为蚂蚁渠道，避免渠道混淆。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: 蚂蚁建档渠道固定
predicate: ChannelArchiveReqDto.channel = 'ALIPAY_ANT'
scope: 支付宝蚂蚁建档入站服务 AlipayAntArchiveService.channelArchive
evidence: code_path:AlipayAntArchiveService.channelArchive
```

[[tables/ChannelArchiveReqDto]] [[rules/渠道固定为 ALIPAY_ANT]]