---
type: concept
title: 影像（媒体/文件/附件）
page_key: concepts/media-image
domain: 文件/附件/媒体
status: draft
aliases: [影像, 媒体, 文件, 附件]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile
maps_to: "MediaFile（lls.media 影像平台模型，modelCode=MA001）"
field_targets: [MediaFile.modelCode]
also_confused_with: [project_file_info（项目运营文件管理表）, AttachmentInfoDTO（表单附件）]
adjudication: boundary
boundary: "‘影像’指影像平台 MediaFile（catgId/busiKey/modelCode）；project_file_info 是项目运营文件元数据表，二者不同源，仅业务上都属“文件”域。"
contract_version: "0.1"
---

# 影像（媒体/文件/附件）

## 业务定位

在口语与需求表述中，“影像”“媒体”“文件”“附件”经常被混用。本页给出本域裁决：当说的是“影像”时，指的是影像平台模型 [[tables/media_file]]（`lls.media`），它通过 `catgId`（分类）、`busiKey`（归属）、`modelCode`（模型，建档固定 `MA001`）三件套被定位。

最容易混淆的有两个邻居：`project_file_info`（[[tables/project_file_info]]，项目运营文件管理表）与 `AttachmentInfoDTO`（表单附件）。它们都不在影像平台上，也不参与影像上传/删除/复制/信息变更事件（见 [[processes/client-media-event-routing]]）。

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：裁决边界来自 [代码] 证据；`AttachmentInfoDTO` 的字段与归属未在本次分析中展开。