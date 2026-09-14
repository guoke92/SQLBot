---
type: rule
title: 影像下载URL生成
page_key: media-download-url
domain: 文件/附件/媒体
status: draft
aliases: [fileUrl 生成, getDownloadUrl 规则, 影像 URL 口径]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:ClientMediaSyncService.java:setInvokeArg
  - code_path:ClientMediaSyncService.java:getRelativePath
contract_version: "0.1"
belong: rules
---

# 影像下载URL生成

## 业务定位

同步下游前，系统按 `path` 生成 `fileUrl`：若 `path` 含 `?` 则截断，并按 `cosHost` 去前缀后调用 `getDownloadUrl`；非全路径则用 `getBrowsUrl`。

对使用方的影响：对外同步出去的 `fileUrl` 统一由 COS 相对路径换取，而不是直接透传入库的 `path`。因此库里存的 `path`（含 http 全路径或带签名参数的情况）与下游拿到的 URL 可能不同形态，排查时必须看生成后的 `fileUrl`。

```ground:rule
name: 影像下载URL生成
content: 同步下游时按 path 生成 fileUrl：path 含 ? 则截断并按 cosHost 去前缀后 getDownloadUrl；非全路径用 getBrowsUrl。
impact: 对外同步的 fileUrl 统一由 COS 相对路径换取。
field_targets:
  - MediaFile.fileUrl
  - MediaFile.path
evidence: "code_path:ClientMediaSyncService.java:setInvokeArg/getRelativePath"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

字段语义见 [[tables/media_file]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。