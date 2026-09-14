---
type: caliber
title: 项目文件类型-审批
page_key: project_file_type_approve
domain: 文件/附件/媒体
status: draft
aliases: [file_type=approve]
oid: 1
scope:
  databases: [unknown]
sources: ["db:project_file_info.file_type"]
contract_version: "0.1"
belong: calibers
---
「审批」类项目运营文件口径，用于项目文件列表的精确筛选。

## 需求背景
本期语义分析未提供需求文档主张；口径来自库表取值证据。

## 版本演进
v0 初版：口径来自 project_file_info.file_type 取值证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 项目文件类型-审批
predicate: project_file_info.file_type = 'approve'
scope: 项目运营文件管理
evidence: db
```

关联：[[project_file_info]]、[[project_file]]、[[project_file_page_query]]。