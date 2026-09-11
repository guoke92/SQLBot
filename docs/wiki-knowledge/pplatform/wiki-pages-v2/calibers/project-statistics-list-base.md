---
type: caliber
title: 项目立项统计列表基础口径
page_key: caliber.project-statistics-list-base
domain: 项目报表/统计/上报
status: draft
aliases:
  - 立项统计基础口径
  - 金融科技业务 SaaS 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
---

# 项目立项统计列表基础口径

立项统计页的列表、导出、下拉字典与提醒都以同一组过滤条件为底座：审批类型固定为「金融科技业务」，系统交付类型限定在 SaaS / Saas+本地化。该底座作用在 [[tables/wechat_project_approval_apply]] 上，是全站统计范围的第一道收口。

## 需求背景

业务上只统计金融科技业务线且以 SaaS 形态交付的立项，避免把其他审批类型与本地化-only 交付混入统计。审批通过与否在此之上另行叠加（见 [[calibers/project-ledger-approved]]）；缺方案经理提醒同样复用该底座（见 [[calibers/missing-solution-manager-remind]]）。字段取值定义见 [[tables/wechat_project_approval_apply]]。

## 版本演进

`saaS / Saas+本地化` 的并列取值说明交付形态至少经历一次扩充（从纯 SaaS 到含本地化的混合交付）；sp_type 的过滤值以中文字面量写死在查询中，尚无字典化证据。

```ground:caliber
name: "项目立项统计列表基础口径"
predicate: "wechat_project_approval_apply.sp_type = '金融科技业务' AND wechat_project_approval_apply.system_delivery IN ('SaaS','Saas+本地化')"
scope: "项目立项统计页列表/导出/字典/提醒"
evidence: "code_path:ProjectStatisticsApplication.java:buildPageWrapper + ProjectStatisticsApplication.java:listDistinctMainProjectNamesFinTechSaasApproved"
```