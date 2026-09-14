---
type: rule
title: 项目文件分页查询
page_key: project_file_page_query
domain: 文件/附件/媒体
status: draft
aliases: [项目文件列表查询]
oid: 1
scope:
  databases: [unknown]
sources: ["code:ProjectFileController.java:buildQueryWrapper"]
contract_version: "0.1"
belong: rules
---
按 projectId、fileType 精确查询，title/content 模糊查询，按 updateTime 倒序，支撑项目运营文件列表页（[[project_file]]）。涉及类型口径见 [[project_file_type_cust]] 等五个文件类型口径。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 buildQueryWrapper 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 项目文件分页查询
content: 按 projectId、fileType 精确查询，title/content 模糊查询，按 updateTime 倒序。
impact: 支撑项目运营文件列表页
field_targets: [project_file_info.project_id, project_file_info.file_type, project_file_info.update_time]
evidence: ProjectFileController.java:buildQueryWrapper
```

关联：[[project_file_info]]、[[project_file]]、[[tenant_project]]。