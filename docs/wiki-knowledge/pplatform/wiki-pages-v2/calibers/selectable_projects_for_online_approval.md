---
type: caliber
title: 可发起上线审批的项目
page_key: selectable_projects_for_online_approval
domain: 微企链立项与项目审批
status: draft
aliases:
  - 历史项目发起上线审批可选范围
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:listApprovalSelectableProjects
contract_version: "0.1"
belong: calibers
---

历史项目发起上线审批时，可选项目的范围口径：项目状态为生效或失效、且记录启用。

```ground:caliber
name: 可发起上线审批的项目
predicate: tenant_project.project_status IN ('EFFECTIVE','INVLIAD') AND tenant_project.enable = 'Y'
scope: 历史项目发起上线审批可选项目
evidence: code_path:ProjectApprovalApplication.java:listApprovalSelectableProjects
```

## 需求背景

该口径作用于 `tenant_project` 表（本次语义分析未产出其字段级释义，见文末 REVIEW），命中后进入上线审批发起流程，见 [[rules/online_approval_submit]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。