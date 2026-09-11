---
type: rule
title: 上线审批通过后自动生效项目
page_key: rules/effective_on_approval_finished
domain: 租户项目
status: draft
aliases: [审批完成生效项目, effectiveProjectOnApprovalFinished]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_project_approval]] 的工作流完成通过后，系统调用 effective 将对应项目置为 EFFECTIVE，形成「审批完成 → 项目生效」的自动链路，连接了 [[processes/project_approval_workflow_status]] 与 [[processes/tenant_project_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则使项目生效可以不由人工直接触发，而是由审批结果驱动。

## 版本演进
项目状态因此存在两条进入 EFFECTIVE 的路径（人工 effective 与审批自动生效），需在审计时区分来源；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 上线审批完成通过后自动生效项目
table: tenant_project
fields: [project_status]
statement: 上线审批完成通过后 effectiveProjectOnApprovalFinished 调 effective
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
```