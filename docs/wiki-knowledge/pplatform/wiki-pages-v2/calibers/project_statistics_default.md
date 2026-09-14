---
type: caliber
title: 项目统计默认范围
page_key: project_statistics_default
domain: 微企链立项与项目审批
status: draft
aliases:
  - 项目统计默认过滤
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:ProjectStatisticsApplication.java:buildPageWrapper
contract_version: "0.1"
belong: calibers
---

项目立项统计列表与导出默认生效的数据范围：只统计金融科技业务类型、且系统交付方式为 SaaS 或 Saas+本地化 的项目。

```ground:caliber
name: 项目统计默认范围
predicate: wechat_project_approval_apply.sp_type = '金融科技业务' AND wechat_project_approval_apply.system_delivery IN ('SaaS','Saas+本地化')
scope: 项目立项统计列表/导出
evidence: code_path:ProjectStatisticsApplication.java:buildPageWrapper
```

## 需求背景

默认范围作用于 [[wechat_project_approval_apply]] 的统计查询构建环节，字段语义见该表页的 `sp_type` 与 `system_delivery`。

## 版本演进

当前语义分析未提供该口径的历史变更记录。