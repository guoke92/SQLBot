---
type: caliber
title: 缺方案经理提醒范围
page_key: missing_solution_manager_remind
domain: 项目报表/统计/上报
status: draft
aliases:
  - 缺方案经理提醒范围
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.listApprovedMissingSolutionManagerForRemind
contract_version: "0.1"
belong: calibers
---

提醒 Job 的取数范围：审批已通过（act_procinst_status='2'）但方案经理为空（solution_manager IS NULL）的立项记录。它是[[concepts/solution_manager|方案经理]]责任人缺失的唯一监控口径，也是[[rules/batch_change_plan_mgr_limit|批量变更方案经理限制]]之外的人员数据质量兜底。

## 需求背景

需求文档未单独描述该提醒口径；范围逐字来自 Job 查询方法。

## 版本演进

v0 契约首版。口径只判 NULL，对空字符串 CSV 不敏感；如需覆盖空串需另行确认。相关：[[processes/act_procinst_status]]、[[tables/wechat_project_approval_apply]]。

```ground:caliber
name: 缺方案经理提醒范围
predicate: "wechat_project_approval_apply.act_procinst_status = '2' AND wechat_project_approval_apply.solution_manager IS NULL"
scope: 提醒Job
evidence: code_path:ProjectStatisticsApplication.listApprovedMissingSolutionManagerForRemind
```