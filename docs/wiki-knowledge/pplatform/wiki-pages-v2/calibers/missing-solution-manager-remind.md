---
type: caliber
title: 缺方案经理提醒口径
page_key: caliber.missing-solution-manager-remind
domain: 项目报表/统计/上报
status: draft
aliases:
  - 缺方案经理提醒
  - remindMissingSolutionManager
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
  - code:ProjectStatisticsRemindApplication.java
contract_version: "0.1"
---

# 缺方案经理提醒口径

每个统计日扫描已审批通过、交付形态在统计范围内、申请时间不早于固定起始日、且尚未维护方案经理的立项，形成企微提醒清单。它是 [[calibers/project-statistics-list-base]] 与 [[calibers/project-ledger-approved]] 的叠加，再补上「方案经理为空」与有效标识两个条件。

## 需求背景

为避免立项通过后长期无人跟进方案，系统每日 10:00 通过企微推送缺方案经理的项目，并支持通过 Nacos 开关 `project.statistics.missing.planmgr.remind.enable` 关闭。方案经理本身的落库需满足企微部门归属校验（见 [[rules/manager-wechat-identity-validation]]），字段定义见 [[tables/wechat_project_approval_apply]]。

## 版本演进

固定起始日的存在说明提醒只覆盖某时间点之后申请的项目，属口径引入时的历史边界；开关化的 Nacos 配置表明该提醒曾因打扰或数据质量原因需要可关闭。

```ground:caliber
name: "缺方案经理提醒口径"
predicate: "sp_type='金融科技业务' AND system_delivery IN ('SaaS','Saas+本地化') AND act_procinst_status='2' AND apply_start_time >= 固定起始日 AND enable='Y' AND solution_manager 为空"
scope: "每日 10:00 企微提醒（可通过 Nacos project.statistics.missing.planmgr.remind.enable 关闭）"
evidence: "code_path:ProjectStatisticsApplication.java:listApprovedMissingSolutionManagerForRemind + ProjectStatisticsRemindApplication.java:remindMissingSolutionManager"
```