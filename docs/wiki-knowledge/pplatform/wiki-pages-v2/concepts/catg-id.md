---
type: concept
title: catgId 影像分类ID
page_key: concepts/catg-id
domain: 文件/附件/媒体
status: draft
aliases: [catgId, 影像分类ID, 影像分类]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code:MediaFile.catgId
maps_to: "MediaFile.catgId（如 A0004/A0049/A0050）"
field_targets: [MediaFile.catgId]
also_confused_with: [modelCode, fileType]
adjudication: boundary
boundary: "catgId 是影像分类维度，modelCode 是模型维度（建档固定 MA001），project_file_info.file_type 是另一套文件模块类型（cust/approve/check/collate/other）。"
contract_version: "0.1"
---

# catgId 影像分类ID

## 业务定位

`catgId` 是影像的分类维度，也是绝大多数影像业务口径的谓词载体：授权书 `A0004`（[[calibers/auth-media-a0004]]）、CA 升级授权书 `A0049`（[[calibers/ca-upgrade-auth-media-a0049]]）、电子签约版授权书 `A0050`（[[calibers/electronic-auth-media-a0050]]）、法人证件 `A0007`/`A0008`（[[calibers/legal-person-cert-media-a0007-a0008]]）、操作人/授权类证件 `A0011`/`A0012`（[[calibers/operator-auth-cert-media-a0011-a0012]]）。分类还支持后缀细分（如 `A000701`、`A001101`），即 `catgId` 自带两级语义。

三个概念不可互译：`catgId`（影像分类）、`modelCode`（影像模型，建档固定 `MA001`）、`project_file_info.file_type`（运营文件模块类型 `cust/approve/check/collate/other`）。把 `file_type` 当成 `catgId` 使用会直接落到另一张表 [[tables/project_file_info]]。

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：边界来自 [代码] 与 [DB] 证据；`catgId` 的完整枚举（含全部后缀）未在本次分析中给出。