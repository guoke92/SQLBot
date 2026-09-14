---
type: rule
title: 项目上线审批打包下载
page_key: project_approval_zip_download
domain: 文件/附件/媒体
status: draft
aliases: [上线审批附件下载]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ProjectMediaFacade.java:streamApprovalMediaZip/resolveApprovalZipFileName"]
contract_version: "0.1"
belong: rules
---
流式将 MA003 影像树写入 zip，按分类目录组织，重名文件加序号，zip 命名为「项目名称+上线审批+yyyymmdd.zip」，支持审批附件一键下载。目录命名依赖 [[media_category_name_fallback]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 streamApprovalMediaZip / resolveApprovalZipFileName 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 项目上线审批打包下载
content: 流式将 MA003 影像树写入 zip，按分类目录组织，重名文件加序号，zip 命名“项目名称+上线审批+yyyymmdd.zip”。
impact: 支持审批附件一键下载
field_targets: [media_file.busi_key, media_file.catg_id]
evidence: ProjectMediaFacade.java:streamApprovalMediaZip/resolveApprovalZipFileName
```

关联：[[media_file]]、[[busi_key]]、[[catg_id]]、[[media_category_name_fallback]]。