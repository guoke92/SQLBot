---
type: caliber
title: 存储类型COS
page_key: 存储类型COS
belong: calibers
domain: 文件媒体与附件
status: published
aliases: []
oid: 1
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---
本页记录口径「存储类型COS」，用于标识影像存储采用对象存储。

## 需求背景
代码证据显示 `MediaFile.storageType = 'COS'` 表示文件存储在对象存储。同步第三方时通过 COS 工具生成签名下载 URL，但保留原始相对路径 `path`/`spath`。

## 版本演进
v0.1 固化当前代码证据。后续可补充其他存储类型的枚举与迁移规则。

```ground:caliber
name: 存储类型COS
predicate: "MediaFile.storageType = 'COS'"
scope: 影像存储类型为对象存储
evidence: code
```