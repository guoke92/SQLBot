---
type: rule
title: 一证四步数据 JSON 深拷贝
page_key: one_cert_four_step_deep_copy
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

该规则要求当一证四步数据非空时，通过 JSON 序列化与反序列化实现深拷贝，并设置到 ChannelOneCertFourStepDto。

## 需求背景

避免请求对象与内部处理对象共享引用，防止后续修改污染原始数据。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: 一证四步数据 JSON 深拷贝
content: 若 req.getOneCertFourStepData() 不为空，通过 JSON.toJSONString 再 parseObject 生成 ChannelOneCertFourStepDto 并设置
impact: 保证一证四步数据深度拷贝，避免引用传递
field_targets: ["oneCertFourStepData"]
evidence: code_path:AlipayAntArchiveService.channelArchive
```

[[tables/AlipayAntCompanyArchiveReq]]