---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:wechat-project-initiation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 字段变更来源
page_key: change_source
domain: 项目审批
aliases:
- 人工编辑
- 同步写入
- 批量变更
- 导入覆盖
- 模拟立项初始写入
anchors:
- change_source
---
# 字段变更来源

wechat_project_approval_field_history.change_source 五值：EDIT 详情页编辑 / BATCH 批量变更（如批量变更方案经理）/ IMPORT 异步导入覆盖 / MANUAL_CREATE 模拟立项初始写入（保证后续不被同步覆盖）/ SYNC 企微同步写入。同步保护判定：字段存在 source≠SYNC 历史时企微同步跳过覆盖。

```ground:enum
enum: change_source
fields:
- wechat_project_approval_field_history.change_source
values:
  EDIT:
    label: 详情页编辑保存
  BATCH:
    label: 批量变更
  IMPORT:
    label: 异步导入覆盖
  MANUAL_CREATE:
    label: 模拟立项初始写入
  SYNC:
    label: 企微同步Job写入
```

## 关联
- [[wechat_project_approval_field_history|wechat_project_approval_field_history]]
