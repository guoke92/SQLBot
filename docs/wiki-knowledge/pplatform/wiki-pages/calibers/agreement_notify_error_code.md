---
type: caliber
title: 协议告知错误码口径
page_key: caliber/agreement_notify_error_code
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该口径定义当错误消息包含“协议告知与影像”或 notifyAgreement 时，映射为错误码 201121。

## 需求背景

协议告知相关错误独立编码，便于快速识别。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: 协议告知错误码口径
predicate: message CONTAINS '协议告知与影像' OR 'notifyAgreement' -> 201121
scope: AntArchiveErrorMapper.mapCaOrBusinessCode
evidence: code_path:AntArchiveErrorMapper.mapCaOrBusinessCode
```

[[tables/AlipayAntArchiveResp]] [[rules/CA 证书错误码显式映射]]