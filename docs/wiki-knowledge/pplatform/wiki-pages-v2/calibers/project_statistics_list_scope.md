---
type: caliber
title: 项目立项统计列表基础范围
page_key: project_statistics_list_scope
domain: 项目报表/统计/上报
status: draft
aliases:
  - 项目立项统计列表基础范围
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:ProjectStatisticsApplication.buildPageWrapper
contract_version: "0.1"
belong: calibers
---

这是项目立项统计页列表的基线过滤条件：只看审批类型为「金融科技业务」且交付方式属于 SaaS 与 Saas+本地化的记录。该条件由 buildPageWrapper 统一拼装，页面上任何二次筛选都建立在此范围之上，因此统计口径的分子分母都以它为先决条件。

## 需求背景

需求文档未单独给出该口径描述；口径内容逐字来自代码构建的分页条件。

## 版本演进

v0 契约首版。注意 system_delivery 的两个取值大小写敏感（'SaaS' 与 'Saas+本地化'），后续若新增交付方式需同步本口径，否则会从统计范围中静默丢失。相关：[[tables/wechat_project_approval_apply]]、[[calibers/missing_solution_manager_remind]]。

```ground:caliber
name: 项目立项统计列表基础范围
predicate: "wechat_project_approval_apply.sp_type = '金融科技业务' AND wechat_project_approval_apply.system_delivery IN ('SaaS','Saas+本地化')"
scope: 项目立项统计页列表
evidence: code_path:ProjectStatisticsApplication.buildPageWrapper
```