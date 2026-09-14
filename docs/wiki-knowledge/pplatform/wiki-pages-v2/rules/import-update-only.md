---
type: rule
title: 导入仅支持更新（正式链路）
page_key: import-update-only
domain: 项目报表/统计/上报
status: draft
aliases:
  - 导入更新规则
  - 正式导入链路
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
belong: rules
---

# 导入仅支持更新（正式链路）

正式导入链路不对不存在的单据做新增，只按 spNo 匹配库中已存在的记录做更新。该限制把「新建」收口在企微同步与模拟立项两条路径上，避免导入制造脏数据。

## 需求背景

立项单据的主键语义来自企微审批（spNo），导入主要用于批量维护统计侧字段（方案经理、前方案经理、首笔落地时间等）。若允许导入新增，将出现无审批来源的立项，破坏审批通过口径（见 [[calibers/project-ledger-approved]]）。导入涉及的字段写入同样受白名单与字段历史约束（见 [[rules/edit-whitelist-and-field-history]]），批量变更来源记为 IMPORT（见 [[tables/wechat_project_approval_apply_field_history]]）。

## 版本演进

正式链路限定「仅更新」，而开发用导入链路另有建单能力（见 [[processes/project-data-source]]），二者按环境分离；该规则的完整约束内容在语义分析中被截断，影响面待补证。

```ground:rule
name: "导入仅支持更新（正式链路）"
content: "项目立项统计正式导入以 spNo 匹配库中已存在记"
impact: "待补证（语义分析中该规则内容被截断）"
field_targets:
  - "wechat_project_approval_apply.sp_no"
evidence: "code_path:ProjectStatisticsApplication.java（导入链路，语义分析未给出方法名）"
```