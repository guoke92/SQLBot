---
type: concept
title: 附件
page_key: attachment
domain: 文件/附件/媒体
status: draft
aliases: [attachment, 附件信息]
oid: 1
scope:
  databases: [unknown]
sources: ["term_bridge:附件", "code:AttachMentFacade/AttachmentInfoProvider"]
contract_version: "0.1"
maps_to: attachment_info
adjudication: boundary
field_targets: []
also_confused_with: [影像, 项目文件]
belong: concepts
---
附件通过 AttachMentFacade/AttachmentInfoProvider 查询，用于表单模板附件；与影像树（[[media]]）、项目文件（[[project_file]]）不是同一套存储。本概念以边界判定为主，不建立同义关系。

## 需求背景
本期语义分析未提供需求文档主张；本概念来自术语桥证据。

## 版本演进
v0 初版：确立附件＝attachment_info 的边界判定；本期未获得附件字段级证据，故 frontmatter 未列 field_targets；无 action=uncovered 的文档主张。

关联：[[attachment_info]]、[[media]]、[[project_file]]。