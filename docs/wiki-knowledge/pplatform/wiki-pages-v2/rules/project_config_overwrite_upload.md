---
type: rule
title: 项目配置文件覆盖上传
page_key: project_config_overwrite_upload
domain: 文件/附件/媒体
status: draft
aliases: [项目配置影像覆盖]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ProjectMediaFacade.java:uploadProjectConfigFiles"]
contract_version: "0.1"
belong: rules
---
上传项目配置文件到影像树前，先删除该 projectApprovalId 下 PROJECT_CONFIG 分类的所有影像，再写入新文件，保证同项目重复推送时配置目录不残留旧文件。与「只增不删」的 [[electronic_auth_incremental_upload]] 形成对照。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 uploadProjectConfigFiles 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 项目配置文件覆盖上传
content: 上传项目配置文件到影像树前，先删除该 projectApprovalId 下 PROJECT_CONFIG 分类的所有影像，再写入新文件。
impact: 保证同项目重复推送时配置目录不残留旧文件
field_targets: [media_file.busi_key, media_file.catg_id]
evidence: ProjectMediaFacade.java:uploadProjectConfigFiles
```

关联：[[media_file]]、[[busi_key]]、[[catg_id]]、[[electronic_auth_incremental_upload]]。