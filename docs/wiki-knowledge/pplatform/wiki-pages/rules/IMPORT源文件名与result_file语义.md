---
type: rule
title: IMPORT 源文件名与 result/file 语义
page_key: IMPORT源文件名与result_file语义
domain: 异步任务与数据同步
status: published
aliases: []
oid: 1
sources: ["code"]
contract_version: "0.1"
field_targets: [async_io_task.file_name, async_io_task.file_url, async_io_task.task_type]
scope:
  databases: [lowcode_pplatform]
---

该规则规定 IMPORT/EXPORT 登记时 file_name 与 file_url 的初始值，避免导入源文件被误认为结果文件。相关表：[[async_io_task]]。

## 需求背景

导入任务与导出任务的文件语义不同，需要区分。

## 版本演进

v0.1 提取。

```ground:rule
name: IMPORT 源文件名与 result/file 语义
content: IMPORT 登记时只写入 file_name（用户上传源文件名），file_url 留空；EXPORT 登记时 file_name 和 file_url 均留空。成功后 export 写生成文件，导入失败写错误文件
impact: 避免将导入源文件当成结果文件下载
field_targets:
  - async_io_task.task_type
  - async_io_task.file_name
  - async_io_task.file_url
evidence: code_path:AsyncIoTaskManager.createPending
```