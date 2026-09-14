---
type: rule
title: 项目运营文件分页查询规则
page_key: project-file-page-query
domain: 文件/附件/媒体
status: draft
aliases: [项目运营文件列表口径, buildQueryWrapper 规则, 项目文件检索口径]
oid: 1
scope:
  databases: [project_file_info]
sources:
  - code_path:ProjectFileController.java:buildQueryWrapper
contract_version: "0.1"
belong: rules
---

# 项目运营文件分页查询规则

## 业务定位

项目运营文件列表的检索口径是：`projectId`、`fileType` 为等值过滤，`title`、`content` 为模糊过滤，结果按 `updateTime` 倒序。

这决定了使用方式：先用“项目 + 模块类型”精确定位一个范围，再用标题/描述做模糊收窄；因为排序键是 `updateTime`，列表的“最新”语义是“最近被编辑过”，而不是“最近创建”。

```ground:rule
name: 项目运营文件分页查询规则
content: projectId、fileType 为等值过滤，title、content 为模糊过滤，按 updateTime 倒序。
impact: 列表检索口径：项目+模块类型精确定位，标题/描述模糊。
field_targets:
  - project_file_info.project_id
  - project_file_info.file_type
  - project_file_info.title
  - project_file_info.content
evidence: "code_path:ProjectFileController.java:buildQueryWrapper"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

字段语义见 [[tables/project_file_info]]；写入语义见 [[rules/project-file-save-or-update]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。