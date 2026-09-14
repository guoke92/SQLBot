---
type: rule
title: 影像分类名称回退
page_key: media_category_name_fallback
domain: 文件/附件/媒体
status: draft
aliases: [分类名称回退]
oid: 1
scope:
  databases: [unknown]
sources: ["code:MediaFacade.java:getMediaCategoryDisplayName"]
contract_version: "0.1"
belong: rules
---
获取影像分类中文名失败或为空时回退返回 catgId 本身（[[catg_id]]），保证打包下载时目录名不丢失。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 getMediaCategoryDisplayName 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 影像分类名称回退
content: 获取影像分类中文名失败或为空时，回退返回 catgId 本身。
impact: 保证打包下载时目录名不因分类查询失败而丢失
field_targets: [media_file.catg_id]
evidence: MediaFacade.java:getMediaCategoryDisplayName
```

关联：[[media_file]]、[[catg_id]]、[[project_approval_zip_download]]。