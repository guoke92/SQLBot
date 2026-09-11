---
type: table
title: project_file_info 项目运营文件表
page_key: tables/project_file_info
domain: 文件/附件/媒体
status: draft
aliases: [项目运营文件表, 项目文件信息表, 运营文件]
oid: 1
scope:
  databases: [project_file_info]
sources:
  - db:project_file_info
  - code_path:ProjectFileController.java:saveOrUpdate
  - code_path:ProjectFileController.java:buildQueryWrapper
contract_version: "0.1"
---

# project_file_info 项目运营文件表

## 业务定位

`project_file_info` 是项目运营侧的文件元数据表：它只保存“文件在项目里的登记信息”（标题、描述、模块类型、归属项目），不保存影像本体，也不承载影像平台的上传/删除事件。业务上它以项目（`project_id` → `tenant_project`）为聚合根，按 `file_type` 划分到客户资料/审批/核对/核查/其他等模块，供项目运营人员登记与检索资料。

它最容易与影像平台模型 [[tables/media_file]] 混淆：两者都落在“文件”域，但 `project_file_info` 是运营文件登记表（`title`/`content`/`file_type`），[[tables/media_file]] 是影像平台模型（`catgId`/`busiKey`/`modelCode`），二者不同源。术语边界见 [[concepts/media-image]] 与 [[concepts/catg-id]]。

写入与读取语义分别由 [[rules/project-file-save-or-update]] 和 [[rules/project-file-page-query]] 约束。

```ground:fields
fields:
  - name: id
    meaning: 表主键，项目运营文件记录ID（ProjectFileController.saveOrUpdate 时报文 id 不能为空）
    evidence: db
  - name: title
    meaning: 文件标题，列表支持模糊查询
    evidence: db
  - name: content
    meaning: 文件描述/内容，列表支持模糊查询
    evidence: db
  - name: file_type
    meaning: 文件模块类型；实测值域 cust=客户资料、approve=审批、collate=核对/整理、check=核查、other=其他
    evidence: db
  - name: project_id
    meaning: 关联项目ID（指向 tenant_project 项目），分页查询的精确匹配条件
    evidence: db
  - name: enable
    meaning: 逻辑启用标识，默认 Y
    evidence: db
  - name: code
    meaning: 编码
    evidence: db
  - name: name
    meaning: 名称
    evidence: db
  - name: create_by
    meaning: 创建人id
    evidence: db
  - name: create_user
    meaning: 创建人名称
    evidence: db
  - name: update_by
    meaning: 更新人id
    evidence: db
  - name: update_user
    meaning: 更新人名称
    evidence: db
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据，需求侧口径待补充。）

从字段结构可读出的业务意图：`title`/`content` 承担“人读的检索入口”，因此列表检索把二者做成模糊条件；`project_id` 与 `file_type` 承担“机器定位入口”，因此是等值条件。`file_type` 的值域是运营文件自己的模块划分，与影像分类 [[concepts/catg-id]]、影像模型 `modelCode` 都不是同一套枚举，不可互相翻译。

## 版本演进

- v0（本页）：仅依据 [DB] 字段语义与代码侧读写规则（[[rules/project-file-save-or-update]]、[[rules/project-file-page-query]]）建立契约草稿。
- 字段级的中文注释存在较弱的通用字段（`code`/`name`/`enable`/审计字段）含义未细化，属已知留白。