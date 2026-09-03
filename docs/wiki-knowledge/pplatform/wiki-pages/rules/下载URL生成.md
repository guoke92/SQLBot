---
type: rule
title: 下载URL生成
page_key: 下载URL生成
domain: 文件媒体与附件
status: published
aliases: []
oid: 1
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---
本页记录规则「下载URL生成」。该规则用于同步影像到第三方时生成可访问下载地址，同时保留原始路径信息。

## 需求背景
代码路径 `ClientMediaSyncService.java:setInvokeArg` 显示：同步影像到第三方时，通过 COS 工具生成带签名的下载 URL，但保留 `path`/`spath` 为原始相对路径。该规则与 [[存储类型COS]]、[[影像变动同步第三方]] 直接衔接。

## 版本演进
v0.1 固化当前代码规则。注意 `MediaFile.fileUrl` 当前出现在规则字段目标中，但尚未进入 [[影像]] 字段语义清单，后续版本需补齐。

```ground:rule
name: 下载URL生成
content: "同步影像到第三方时，通过COS工具生成带签名的下载URL，但保留path/spath为原始相对路径"
impact: "第三方可访问文件，同时保留原始路径信息"
field_targets:
  - MediaFile.path
  - MediaFile.fileUrl
evidence: "code_path:ClientMediaSyncService.java:setInvokeArg"
```