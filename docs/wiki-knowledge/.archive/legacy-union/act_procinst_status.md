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
title: 企微审批状态
page_key: act_procinst_status
domain: 项目审批
aliases:
- 审批中
- 已通过
- 已撤销
- 挂起
- 企微审批原码
- sp_status
- 审批状态原码
anchors:
- act_procinst_status
---
# 企微审批状态

act_procinst_status 即企微 sp_status 原码（无转换直存）：1 审批中、2 已通过、3 已拒绝、4 已撤销、6 通过后撤销、7 已删除。统计页默认可见 {1,2}；导出固定过滤 ='2' AND data_source='WECHAT'。增量同步排除非审批中（≠1）的已有记录。

```ground:enum
enum: act_procinst_status
fields:
- wechat_project_approval_apply.act_procinst_status
values:
  '1':
    label: 审批中
  '2':
    label: 已通过
  '3':
    label: 已拒绝
  '4':
    label: 已撤销
  '6':
    label: 通过后撤销
  '7':
    label: 已删除
```

## 关联
- [[wechat_project_approval_apply|wechat_project_approval_apply]]
