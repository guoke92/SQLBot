---
type: concept
title: 影像
page_key: media
domain: 文件/附件/媒体
status: draft
aliases: [media, 客户影像, 影像文件]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:影像", "code:MediaFacade/CustMediaFacade/IMediaOperaProvider"]
contract_version: "0.1"
maps_to: media_file
adjudication: synonym
field_targets: [media_file.catg_id, media_file.busi_key, media_file.user_busi_key]
also_confused_with: [附件, 项目文件]
belong: concepts
---
影像指通过 MediaFacade/CustMediaFacade 管理的客户文件，底层由 IMediaOperaProvider 维护，分类使用 catgId（[[catg_id]]），业务归属用 busiKey（[[busi_key]]）。影像与 [[attachment]]、[[project_file]] 是三套不同存储，容易混淆，判据见下。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立「影像」为 media_file 的同义词，并与附件、项目文件做边界切分；无 action=uncovered 的文档主张。

边界：影像走 MediaFacade/CustMediaFacade + IMediaOperaProvider，分类用 catgId；附件走 AttachMentFacade/AttachmentInfoProvider；项目文件是 [[project_file_info]] 的元数据记录。

关联：[[media_file]]、[[attachment]]、[[project_file]]、[[catg_id]]、[[busi_key]]。