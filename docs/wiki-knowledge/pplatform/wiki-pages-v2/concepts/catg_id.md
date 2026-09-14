---
type: concept
title: catgId（影像分类）
page_key: catg_id
domain: 文件/附件/媒体
status: draft
aliases: [分类ID, 影像分类]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:catgId", "code:MediaFacade.java:getMediaCategoryDisplayName", "code:CustMediaFacade.java:uploadElectronicAuthMediaFile"]
contract_version: "0.1"
maps_to: media_file.catg_id
adjudication: boundary
field_targets: [media_file.catg_id]
also_confused_with: [fileType]
belong: concepts
---
catgId 是影像分类编码（如 A0004 授权书、A0007 法人证件等），落在 [[media_file]].catg_id 上；按操作人过滤、分类名回退等规则都以此为键，口径见 [[media_catg_a0004]]、[[media_catg_a0049]]、[[media_catg_a0050]]。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立 catgId 与 fileType 的边界（前者影像分类编码，后者为 [[project_file_info]].file_type 的文件模块类型）；无 action=uncovered 的文档主张。

关联：[[media_file]]、[[media]]、[[catg_operator_filter]]、[[media_category_name_fallback]]。