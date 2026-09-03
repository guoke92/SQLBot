---
type: caliber
title: 影像文件错误码口径
page_key: caliber/image_file_error_code
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该口径定义当错误消息包含 sftp、SFTP 或“影像文件”时，映射为错误码 201120。

## 需求背景

影像文件相关错误需要独立错误码，便于定位问题域。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: 影像文件错误码口径
predicate: message CONTAINS 'sftp' OR 'SFTP' OR '影像文件' -> 201120
scope: AntArchiveErrorMapper.mapCaOrBusinessCode
evidence: code_path:AntArchiveErrorMapper.mapCaOrBusinessCode
```

[[tables/AlipayAntArchiveResp]] [[rules/CA 证书错误码显式映射]]