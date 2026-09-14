---
type: caliber
title: 项目台账导出企业source判定
page_key: project_ledger_export_source
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目台账导出企业source判定
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectReportApplication.exportProjectReport
contract_version: "0.1"
belong: calibers
---

导出项目台账时，企业行的「数据来源」列由 [[tables/tenant_project|tenant_project]].channel 三分法判定：等于 '产融平台' 输出「产融」，其余一律输出「讯易链」。这是一个兜底式二分，值域中不存在第三类展示文案。

## 需求背景

需求文档未单独描述该判定；口径逐字来自导出方法中的三元表达式。

## 版本演进

v0 契约首版。该口径与 [[concepts/chanrong|产融]]/讯易链的数据来源边界直接对应：产融走本地表 cust_project_rel，讯易链走洞察平台。若未来新增渠道，需先改造本判定再新增来源文案。

```ground:caliber
name: 项目台账导出企业source判定
predicate: "tenant_project.channel = '产融平台' ? '产融' : '讯易链'"
scope: 导出时企业数据来源
evidence: code_path:ProjectReportApplication.exportProjectReport
```