---
type: dict
title: project_file_info.file_type
page_key: project_file_info__file_type
belong: dicts
status: draft
anchors: [project_file_info.file_type]
sources: ['database_profile:project_file_info.file_type']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [project_file_info]
---

# project_file_info.file_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `project_file_info.file_type`，表页 [[tables/project_file_info]]。

## 取值

```ground:dict
dict: project_file_info__file_type
fields: [project_file_info.file_type]
values:
  cust: {trust: proposed}
  approve: {trust: proposed}
  collate: {trust: proposed}
  other: {trust: proposed}
  check: {trust: proposed}
triage: keep
```
