---
type: rule
title: 项目运营文件保存/更新规则
page_key: project-file-save-or-update
domain: 文件/附件/媒体
status: draft
aliases: [项目运营文件保存规则, saveOrUpdate 规则]
oid: 1
scope:
  databases: [project_file_info]
sources:
  - code_path:ProjectFileController.java:saveOrUpdate
contract_version: "0.1"
belong: rules
---

# 项目运营文件保存/更新规则

## 业务定位

`project_file_info` 的新增与编辑共用一个入口：`saveOrUpdate` 要求入参 `id` 不能为空；按 `id` 查得记录则仅更新 `title`、`content` 及更新人/时间；查不到则按入参新增并写入创建人/时间。

对使用方的直接影响：能否“保存成功”取决于 `id` 是否命中既有记录，而不是内容是否重复——因此该接口不能被当作“按标题去重写入”的手段。

```ground:rule
name: 项目运营文件保存/更新规则
content: saveOrUpdate 要求入参 id 不能为空；按 id 查得记录则仅更新 title、content 及更新人/时间；查不到则按入参新增并写入创建人/时间。
impact: 项目运营文件的新增与编辑语义由是否存在记录决定，不能用于按标题去重。
field_targets:
  - project_file_info.id
  - project_file_info.title
  - project_file_info.content
evidence: "code_path:ProjectFileController.java:saveOrUpdate"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

表结构见 [[tables/project_file_info]]；列表读取口径见 [[rules/project-file-page-query]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。