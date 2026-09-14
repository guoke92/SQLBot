---
type: caliber
title: 审批中记录
page_key: approving_apply_records
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微审批中记录
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:validateAndApply
contract_version: "0.1"
belong: calibers
---

项目立项统计导入时用于识别并跳过「企微审批中」记录的口径：状态为审批中的申请不进入统计导入。

```ground:caliber
name: 审批中记录
predicate: wechat_project_approval_apply.act_procinst_status = '1'
scope: 项目立项统计导入跳过审批中记录
evidence: code_path:ProjectStatisticsApplication.java:validateAndApply
```

## 需求背景

该口径与导出口径互补：导出取已通过（2），统计导入跳过审批中（1）。状态取值见 [[processes/wechat_apply_approval_status]]，所在表见 [[wechat_project_approval_apply]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。