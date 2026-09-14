---
type: caliber
title: 口径：项目已生效
page_key: project_effective
domain: 租户项目
status: draft
aliases: [项目已生效, 已生效项目]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
  - code:ProjectReportApplication
contract_version: "0.1"
belong: calibers
---

判定 [[tenant_project]] 中已生效的项目，对应 [[ProjectStatusEnum]] 的 1。导出侧按 1 直接转"已生效"，因此该口径同时是报表口径，流转见 [[tenant_project_status]]。

## 需求背景
语义分析未附带需求文档锚点；只有已生效项目才允许被业务单据引用。

## 版本演进
语义分析未记录该口径的版本演进。

```ground:caliber
name: 项目已生效
predicate: "tenant_project.project_status = '1'"
scope: tenant_project
evidence: "code:ProjectStatusEnum.EFFECTIVE; ProjectReportApplication 按 1 转已生效"
```