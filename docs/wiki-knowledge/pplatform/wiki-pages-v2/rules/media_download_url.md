---
type: rule
title: 影像下载URL生成
page_key: media_download_url
domain: 文件/附件/媒体
status: draft
aliases: [影像URL生成]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ClientMediaSyncService.java:setInvokeArg/getRelativePath"]
contract_version: "0.1"
belong: rules
---
同步影像到第三方时，对相对路径生成 COS 下载 URL；若 path 含 `?` 则截取并去掉 COS host，保证第三方可下载影像。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 setInvokeArg / getRelativePath 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 影像下载URL生成
content: 同步影像到第三方时，对相对路径生成 COS 下载 URL；若 path 含 ? 则截取并去掉 COS host。
impact: 保证第三方能通过 URL 下载影像
field_targets: [media_file.path, PlatFormMediaFileDTO.file_url]
evidence: ClientMediaSyncService.java:setInvokeArg/getRelativePath
```

关联：[[media_file]]、[[media]]。