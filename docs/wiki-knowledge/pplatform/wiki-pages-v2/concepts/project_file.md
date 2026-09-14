---
type: concept
title: 项目文件
page_key: project_file
domain: 文件/附件/媒体
status: draft
aliases: [project file, 项目运营文件]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:项目文件", "code:ProjectFileController.java:buildQueryWrapper"]
contract_version: "0.1"
maps_to: project_file_info
adjudication: boundary
field_targets: [project_file_info.project_id, project_file_info.file_type, project_file_info.update_time]
also_confused_with: [影像, 附件]
belong: concepts
---
项目文件指 [[project_file_info]] 中登记的项目运营文件元数据（标题、描述、类型、关联项目ID），文件实体仍在对象存储；按 [[project_file_info]].file_type 分五类，口径见 [[project_file_type_cust]]、[[project_file_type_approve]]、[[project_file_type_check]]、[[project_file_type_collate]]、[[project_file_type_other]]。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立项目文件＝project_file_info 的边界判定，与影像树、附件区分；无 action=uncovered 的文档主张。

关联：[[project_file_info]]、[[media]]、[[attachment]]、[[project_file_page_query]]。