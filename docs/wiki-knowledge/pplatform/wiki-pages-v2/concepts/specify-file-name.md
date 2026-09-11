---
type: concept
title: specifyFileName 指定文件名
page_key: concepts/specify-file-name
domain: 文件/附件/媒体
status: draft
aliases: [specifyFileName, 指定文件名]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.specifyFileName
maps_to: "MediaFile.specifyFileName"
field_targets: [MediaFile.specifyFileName]
also_confused_with: [fileRename, fileName]
adjudication: boundary
boundary: "specifyFileName 为业务指定名（常不带后缀），fileRename 为展示名，fileName 为原始文件名。"
contract_version: "0.1"
---

# specifyFileName 指定文件名

## 业务定位

`specifyFileName` 是业务语义名（通常不带后缀），在 [[tables/media_file]] 的命名三兄弟中承担“业务怎么称呼这份影像”。边界：`fileRename` 是展示名/重命名后的名称，`fileName` 是原始文件名（`A0004` 缺省时置为“授权书.pdf”）。

它同时是若干业务规则的参与字段：A0004 的默认命名口径（[[rules/auth-media-default-file-name]]）与 A0050 的幂等命中键（[[rules/electronic-auth-media-idempotent]]，命中组合为 `busiKey`/`userBusiKey`/`specifyFileName`）。

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：边界来自 [代码] 证据。