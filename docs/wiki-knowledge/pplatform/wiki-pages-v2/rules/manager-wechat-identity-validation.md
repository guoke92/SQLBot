---
type: rule
title: 方案经理/业务经理企微身份校验
page_key: manager-wechat-identity-validation
domain: 项目报表/统计/上报
status: draft
aliases:
  - 部门归属校验
  - validateImportManagerDeptMembership
  - changeOnePlanMgr
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectStatisticsApplication.java
contract_version: "0.1"
belong: rules
---

# 方案经理/业务经理企微身份校验

方案经理与业务经理的姓名不能随意填写：必须能在企微通讯录中找到，且分别归属指定部门（方案经理归属「Saas方案部」，业务经理归属「客户营销」部，部门名由 Nacos 配置）。校验通过后由企微 userId 反查姓名并落库。

## 需求背景

立项统计需要按人检索与提醒，因此经理字段必须与企微身份对齐。落库时同时维护 solution_manager（姓名 CSV）与 solution_manager_wxid（userId JSON 数组冗余列），后者用于按 wxid 精确过滤（见 [[tables/wechat_project_approval_apply]]）。规则作用于编辑保存、批量变更方案经理、导入、模拟立项四条路径；经理变更还会触发前方案经理合并（见 [[rules/old-solution-manager-merge]]）。

## 版本演进

部门名通过 Nacos 配置（wechat.org.dept.name.saas.solution、wechat.org.dept.name.customer.marketing）而非硬编码，说明组织调整已可通过配置适配；userId 冗余列的引入是为支持按人精确过滤的后期增强。

```ground:rule
name: "方案经理/业务经理企微身份校验"
content: "方案经理姓名须在企微通讯录存在且属于「Saas方案部」（Nacos wechat.org.dept.name.saas.solution）；业务经理姓名须属于「客户营销」部（wechat.org.dept.name.customer.marketing）。落库时由企微 userId 反查姓名 CSV，并同步维护 solution_manager_wxid 冗余列。"
impact: "编辑保存、批量变更方案经理、导入、模拟立项"
field_targets:
  - "wechat_project_approval_apply.solution_manager"
  - "wechat_project_approval_apply.solution_manager_wxid"
  - "wechat_project_approval_apply.bussiness_manager"
  - "wechat_project_approval_apply.business_center"
evidence: "code_path:ProjectStatisticsApplication.java:validateImportManagerDeptMembership + ProjectStatisticsApplication.java:changeOnePlanMgr"
```