---
type: table
title: 附件信息表
page_key: attachment_info
domain: 文件/附件/媒体
status: draft
aliases: [attachment_info, 表单附件表]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:AttachMentFacade/AttachmentInfoProvider（术语桥证据）"]
contract_version: "0.1"
belong: tables
---
attachment_info 是「附件」（[[attachment]]）的存储表，通过 AttachMentFacade/AttachmentInfoProvider 查询，用于表单模板附件；与影像树 [[media_file]]、项目文件 [[project_file_info]] 属于三套不同存储。

## 需求背景
本期语义分析未提供需求文档主张；本页业务定位来自术语桥证据。

## 版本演进
v0 初版：本表未获得字段级语义证据，故不产出 ground:table 锚点块（见 REVIEW）。

关联：[[attachment]]、[[media]]、[[project_file]]。